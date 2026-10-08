from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.linalg import lstsq


def load_counts(data_root):
    guide_table = pd.read_csv(data_root / "guide_gene_barcode_map.tsv.gz", sep="\t", header=None)
    guide_ids = np.array(sorted(guide_table.iloc[:, 1].astype(str)))
    table = pd.read_csv(data_root / "k562_dual_guide_counts.tsv.gz", sep="\t", header=[0, 1, 2, 3], index_col=0)
    ordering = pd.Index(["++".join(pair) for pair in pd.MultiIndex.from_product([guide_ids, guide_ids])])
    if not table.index.is_unique or len(table) != len(ordering) or set(table.index) != set(ordering):
        raise ValueError("Reference raw-count identity universe mismatch")
    values = table.loc[ordering]
    screens = {}
    for replicate in ["rep1", "rep2"]:
        screens[replicate] = (
            values["K562", "barcode", "T0", replicate].to_numpy(dtype=float).reshape(len(guide_ids), len(guide_ids)),
            values["K562", "tripleseq", "cyc", replicate].to_numpy(dtype=float).reshape(len(guide_ids), len(guide_ids)),
        )
    return guide_ids, screens


def independent_phenotypes(guide_ids, raw_screen, replicate, omit):
    keep = np.where(guide_ids != omit)[0] if omit is not None else np.arange(len(guide_ids))
    initial = raw_screen[0][keep][:, keep]
    endpoint = raw_screen[1][keep][:, keep]
    identifiers = guide_ids[keep]
    retained = np.minimum(np.median(endpoint, axis=0), np.median(endpoint, axis=1)) >= 35
    initial = initial[retained][:, retained]
    endpoint = endpoint[retained][:, retained]
    identifiers = identifiers[retained]
    negative_positions = [index for index, identifier in enumerate(identifiers) if identifier.startswith("negative_")]
    if len(negative_positions) < 2:
        raise ValueError("Reference has insufficient negative controls")
    adjusted_initial = initial + 10
    adjusted_endpoint = endpoint + 10
    log_ratio = np.log2(adjusted_endpoint) - np.log2(adjusted_initial)
    log_ratio += np.log2(adjusted_initial.sum()) - np.log2(adjusted_endpoint.sum())
    negative_center = np.median(log_ratio[negative_positions][:, negative_positions])
    result = (log_ratio - negative_center) / (6.91 if replicate == "rep1" else 7.61)
    return identifiers, result


def independent_fit(identifiers, phenotypes):
    measured = np.mean(np.stack([phenotypes, phenotypes.T]), axis=0)
    negative = np.array([identifier.startswith("negative_") for identifier in identifiers])
    row_single = np.average(measured[:, negative], axis=1)
    column_single = np.average(measured[negative, :], axis=0)
    results = []
    for observations, singles, offsets in [(measured, row_single, column_single),
                                          (measured.T, column_single, row_single)]:
        design = np.stack([np.square(singles), singles], axis=1)
        coefficients, _, rank, _ = lstsq(design, observations - offsets, lapack_driver="gelsy")
        if rank != 2:
            raise ValueError("Reference rank-deficient expected phenotype fit")
        predicted = coefficients.T @ design.T + offsets[:, None]
        residual = observations.T - predicted
        negative_residuals = residual[:, negative]
        mean_residual = np.mean(negative_residuals, axis=1, keepdims=True)
        scale = np.sqrt(np.sum(np.square(negative_residuals - mean_residual), axis=1) / (negative.sum() - 1))
        if np.any(scale <= 0) or not np.isfinite(scale).all():
            raise ValueError("Reference has undefined residual scale")
        results.append({"expected": predicted.T, "gi": (residual / scale[:, None]).T,
                        "coefficients": coefficients, "scale": scale, "intercepts": offsets})
    averaged_expected = (results[0]["expected"] + results[1]["expected"].T) * 0.5
    averaged_gi = (results[0]["gi"] + results[1]["gi"].T) * 0.5
    expected = (averaged_expected + averaged_expected.T) * 0.5
    scores = (averaged_gi + averaged_gi.T) * 0.5
    labels = pd.Index([identifier.split("_", 1)[0] for identifier in identifiers])
    genes = np.array(sorted(set(labels) - {"negative"}))

    def group_mean(matrix):
        grouped = pd.DataFrame(matrix, index=labels, columns=labels)
        grouped = grouped.groupby(level=0, sort=True).mean()
        grouped = grouped.T.groupby(level=0, sort=True).mean().T
        return grouped.loc[genes, genes].to_numpy()

    gene_scores = group_mean(scores)
    counts = np.array([np.count_nonzero(labels == gene) for gene in genes])
    populations = np.multiply.outer(counts, counts)
    score_frame = pd.DataFrame(scores, index=labels, columns=labels)
    group_centers = score_frame.groupby(level=0).mean().T.groupby(level=0).mean().T
    deviations = scores - group_centers.loc[labels, labels].to_numpy()
    variance = group_mean(deviations ** 2)
    uncertainty = np.zeros_like(variance)
    multiple = populations > 1
    uncertainty[multiple] = np.sqrt(variance[multiple] * populations[multiple] / (populations[multiple] - 1))
    np.fill_diagonal(gene_scores, 0)
    return {
        "gene_ids": genes, "guide_ids": identifiers, "guide_observed": measured,
        "profile_matrix": gene_scores, "observed_double": group_mean(measured),
        "expected_double": group_mean(expected), "uncertainty": uncertainty,
        "guide_count": counts, "directions": results,
    }


def independent_study(guide_ids, raw_screens, omit=None):
    normalized = {replicate: independent_phenotypes(guide_ids, screen, replicate, omit)
                  for replicate, screen in raw_screens.items()}
    output = {replicate: independent_fit(identifiers, phenotypes)
              for replicate, (identifiers, phenotypes) in normalized.items()}
    first_ids, first_matrix = normalized["rep1"]
    second_ids, second_matrix = normalized["rep2"]
    common = np.array(sorted(set(first_ids) & set(second_ids)))
    first_positions = pd.Index(first_ids).get_indexer(common)
    second_positions = pd.Index(second_ids).get_indexer(common)
    shared_phenotype = (first_matrix[first_positions][:, first_positions] +
                        second_matrix[second_positions][:, second_positions]) / 2
    output["combined"] = independent_fit(common, shared_phenotype)
    return output


def eligible_omissions(reference):
    inventories = {}
    for replicate in ["rep1", "rep2"]:
        record = reference[replicate]
        inventories[replicate] = dict(zip(record["gene_ids"], record["guide_count"]))
    genes = sorted(gene for gene, count in inventories["rep1"].items()
                   if count >= 3 and inventories["rep2"].get(gene, 0) >= 3)
    common_guides = sorted(set(reference["rep1"]["guide_ids"]) & set(reference["rep2"]["guide_ids"]))
    return [(gene, guide) for gene in genes for guide in common_guides if guide.split("_", 1)[0] == gene]


def pearson_rows(first, second):
    size = len(first)
    answer = np.empty((size, size), dtype=float)
    second_base = second.copy()
    np.fill_diagonal(second_base, 0)
    for focal in range(size):
        left = np.broadcast_to(first[focal], (size, size)).copy()
        right = second_base.copy()
        left[:, focal] = 0
        right[:, focal] = 0
        np.fill_diagonal(left, 0)
        counts = np.full(size, size - 2, dtype=float)
        counts[focal] = size - 1
        sums_left, sums_right = left.sum(axis=1), right.sum(axis=1)
        covariance = np.sum(left * right, axis=1) - sums_left * sums_right / counts
        variance_left = np.sum(left ** 2, axis=1) - sums_left ** 2 / counts
        variance_right = np.sum(right ** 2, axis=1) - sums_right ** 2 / counts
        valid = (counts >= 2) & (variance_left > 0) & (variance_right > 0)
        answer[focal] = np.nan
        answer[focal, valid] = covariance[valid] / np.sqrt(variance_left[valid] * variance_right[valid])
    return np.clip(answer, -1, 1)
