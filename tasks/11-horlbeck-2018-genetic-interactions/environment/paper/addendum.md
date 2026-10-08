# Study scope, validation experiments, and delivery protocol

## Research scope and inputs

Reconstruct the K562 gene-level interaction study from the supplied raw count and guide-identity files. Recover the scientific processing method from the paper's Methods and figure captions. Do not substitute published predictions or processed interaction scores for computation from counts.

The complete allowed inputs are identified by the data manifest and their byte hashes:

- `/home/data/horlbeck/k562_dual_guide_counts.tsv.gz`: construct counts with assay, timepoint, and replicate identifiers in the original multi-row column header.
- `/home/data/horlbeck/guide_gene_barcode_map.tsv.gz`: guide, target, and barcode identities.
- The supplied paper, input metadata, and the limited numerical conventions in `conventions.json`.

Use the complete supplied input universe. Keep an exclusion ledger for method-required filtering and undefined comparisons. Do not choose a favorable subset after seeing results.

Produce the replicate-averaged gene-level map and continuous profiles, the independent-replicate comparisons in Figures 2D and 2E, the overall profile-correlation distribution relevant to Figure 2F, and the numeric matrix relevant to Figure 2G. Separate these quantities in the report. In particular, a comparison of two gene profiles is not the same quantity as the agreement of profile-correlation values across two biological replicates.

Do not claim recovery of unsupplied complex annotations, author cluster labels, GO enrichment, Jurkat results, later paper figures, or wet-lab validation. The paper's displayed statistics are context, not numbers to copy or optimize toward.

## Independent biological replication

Reconstruct each biological replicate using its own count measurements and independently estimated quantities. Keep the two analyses distinct until comparison. A map reconstructed from combined measurements is not a substitute for either replicate, and combined-data fit parameters must not be reused to manufacture independent-replicate agreement.

Compare compatible identities on the declared common universe and report excluded identities and reasons. Provide numerical evidence for gene-pair GI agreement, agreement of gene-profile correlation values, and each gene's cross-replicate partner-profile agreement. Retain the replicate-averaged analysis separately.

Use correlation together with scale-sensitive discrepancies and coverage. Explain which claims are supported by the comparisons rather than treating a single high correlation as validation of the whole workflow.

## Additional validation experiments

These experiments extend the evidence beyond the scoped paper reconstruction. Their rules are stated here because they are not recoverable from the paper alone.

### Systematic guide omission

The eligible genes are those with at least three guides retained in each independently processed baseline replicate. For every eligible gene, test each guide retained in both baselines as a separate omission. Publish the complete eligible and tested inventories; an empty or incomplete inventory requires an explanation and is not silently treated as successful coverage.

For an omission, exclude every raw construct containing that guide, then rerun the scientific analysis for each affected replicate and the combined study. Recompute quantities whose values depend on the changed input universe. Merely reaveraging cached, baseline-fitted GI values does not constitute this intervention.

Measure changes on the perturbed gene's partner profile and its incident gene pairs. Report local correlation where defined, absolute and relative scale changes, sign changes, and retained coverage. Give the baseline and perturbed numeric values used for these statistics. Whole-map agreement may be reported additionally but cannot replace the local measurements.

Retain failed fits, loss of eligible comparisons, and non-identifiable interventions in the inventory. Evaluate the experiments as evidence about sensitivity; do not discard an omission because it weakens the preferred conclusion.

### Cross-replicate identity-matching null

Using the independently reconstructed baseline replicate maps, test whether a gene's partner profile agrees with its matching identity in the other replicate more than with randomized identities. Randomize the correspondence between focal genes across replicates while leaving the within-replicate maps and biological partner identities unchanged. Apply the same declared comparison and self-component exclusion rules to the observed and randomized matchings.

Generate at least 199 matching permutations using the fixed seed in `conventions.json`. Keep the actual identity mappings so the null is verifiable without depending on a particular random-number library. Report the observed statistic, the complete empirical null distribution, its uncertainty, and how any tail probability is computed.

The statistic is the median of the finite per-focal-gene Pearson correlations between aligned partner profiles. Exclude from each comparison the self components of both focal genes and record its partner coverage. Treat variation in the valid comparison universe as a limitation, not a way to select favorable matchings.

This is one study-level identity-matching diagnostic. Do not represent permutations, overlapping gene pairs, or partner profiles as additional independent biological replicates. If individual-gene significance claims are added, state the multiplicity treatment; those optional claims cannot substitute for the required study-level result.

## Submission and evidence

The only execution entrypoint is `bash /home/submission/reproduce.sh`. It must run offline from source, without interactive steps or downloading study inputs. Keep authored source and static inputs outside `/home/submission/results`, which the verifier deletes before every clean replay.

Write generated evidence under `/home/submission/results/horlbeck_gi_reproduction/`:

| Artifact | Required semantics |
| --- | --- |
| `gene_pair_gi.csv` | Combined-study unordered non-self pairs: `gene_a`, `gene_b`, `observed_double`, `expected_double`, `gi_score`, `uncertainty` |
| `gi_profiles.npz` | Combined-study `gene_ids`, `partner_ids`, and `profile_matrix` with explicit axes |
| `replicates/<replicate_id>/` | Corresponding independently reconstructed pair table and profile arrays for each replicate |
| `replicate_comparisons.csv` | Named comparison, entity identities, statistic, coverage, and any undefined-value reason |
| `omissions/manifest.csv` | Every eligible omission: `run_id`, `gene_id`, `guide_id`, `status`, `reason`, and evidence location |
| `omissions/<run_id>/` | Perturbed replicate and combined outputs, local comparison values, and input/stage lineage |
| `identity_null/mappings.csv` | `permutation_id`, `replicate1_gene`, and `replicate2_gene` for every randomized correspondence |
| `identity_null/statistics.csv` | Observed and randomized statistics, finite comparison counts, seed, and undefined-value reasons |
| `analysis_manifest.json` | Study/replicate/intervention IDs, array axes, file locations, and mappings to intermediate count-derived, guide-level, and fit evidence |
| `methods.md`, `report.md` | Paper-supported method decisions, data exclusions, figure semantics, numerical results, control interpretation, and limitations |
| `input_checksums.json`, `execution_status.json`, `resource_usage.json` | Input/source binding, actual completion and failures, measured runtime and resource use |

Retain the intermediate normalized measurements, guide identities, fitted quantities and diagnostics needed to independently check the processing and distinguish genuine refits from reused outputs. The intermediate file layout and numerical implementation are yours to choose; make their meanings and axes machine-readable in `analysis_manifest.json`.

The numeric verifier reads every intermediate artifact through `analysis_manifest.json`, so that file's *keys* are part of the interface rather than free-form. Declare the study using either of the two accepted vocabularies below; an undeclared or differently named schema is reported as an unresolved evidence contract instead of being scored.

Array-first (`gene_arrays`) schema:

- `gene_arrays`: `{filename, row_axis, column_axis, fields}` for the per-study GI arrays.
- `guide_state`: `{filename}` for the guide-level observed-double evidence.
- `fit_evidence`: `<path>` or `<path>: <column>` for the per-query fit table.
- `replicate_directories`: `{"rep1": "<dir>", "rep2": "<dir>"}` and `combined_directory`: `"<dir>"`.
- `interventions`: one entry per omission with `run_id` and `phase_outputs`.

Stage-first (`stages`) schema:

- `replicates`: `[{"id": "rep1", "path": "<dir>"}, {"id": "rep2", "path": "<dir>"}]`.
- `combined`: `{"path": "<dir>"}`.
- `stages.raw_to_phenotype`: `{"shared": "<file>", "encoding": "<... indexed raw log ratio ...>"}`.
- `stages.phenotype_to_GI`: `{"query_fits": "<file>", "guide_axes": "<file>"}`.
- `axes`: declared axes for the gene-profile arrays and the unordered gene-pair arrays.
- `interventions`: one entry per omission with `run_id` and `evidence_location`.
- `comparisons`: `{"same_gene_replication": "<file>", "local_omission_metrics": "<file>"}`.
- `exclusions`: `{"omission_eligibility": "<file>"}` and `n_biological_replicates`: `2`.

Everything else - file names, directory names, encodings and numerical implementation - remains yours to choose, and the declared axes/meanings must match the arrays actually written.

The numeric artifacts must support the report and figures. Undefined results require explicit reasons, not invented finite values. Preserve authored source and reports that are inputs to replay; write generated reports inside `results`.

## Assessment and execution limits

Assessment covers complete numeric reconstruction, independent replication, systematic local sensitivity, the identity-matching null, and warranted conclusions. Correlation alone does not establish numeric agreement. Honest weak agreement, local instability, or an inconclusive null is not automatically a scientific failure when computation and interpretation are correct.

The supplied runner defines CPU, memory, agent, native-replay, and verifier limits. Infrastructure provisioning is not scientific computation.
