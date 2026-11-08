**Working title: FreshView — Multiview Produce Condition Assessment**

**Project objective**

Build an application that uses photos of different sides of a fruit or vegetable to estimate its visible condition and communicate uncertainty.

The proposed improvement is combining multiple views instead of relying on one photo. Whether this helps—and whether the approach differs sufficiently from prior research—must be established through literature review and experiments.

**1. Features**

| Feature | User experience | Implementation and limits |
|---|---|---|
| **Photo input** | Upload photos of one item. | Start with one supported produce type and a clear background. |
| **Multiview assessment** | Photograph two or three different sides. | Run each view through the same model, then combine predictions. |
| **Freshness rating** | See a defined visual-condition stage. | Use the labels supported by the dataset. Start with apparently fresh/visible spoilage; add intermediate stages only with reliable labels. |
| **Freshness score** | See a simple condition scale alongside the stage. | Define what the scale means. Prediction confidence must not be presented as “percentage fresh.” |
| **Possible error / uncertainty** | See “uncertain” or “another photo needed.” | Use validation data to select thresholds; examine disagreement between views. |
| **Retake guidance** | Receive a prompt to photograph another side or improve image quality. | Begin with simple instructions. Automatic blur or lighting checks are optional additions. |
| **Remaining-life estimate — extension** | See an estimated range under specified storage conditions. | Requires repeated observations until a defined deterioration endpoint. A fresh/rotten dataset alone cannot support this feature. |
| **History — optional** | Compare an item’s earlier and current assessments. | Save item IDs, dates, photos, and predictions locally. |

The application assesses **visible condition**. It cannot certify food safety or determine an exact expiry date from appearance.

**2. Research question**

> Does multiview analysis improve visible produce-condition classification and reduce confident mistakes compared with single-view analysis?

Compare these systems:

| System | Method | Purpose |
|---|---|---|
| **A: Single view** | Classify one predetermined view. | Baseline |
| **B: Multiple views** | Average predictions across two or three views. | Test the benefit of additional views |
| **C: Multiple views with uncertainty handling** | Combine views and abstain when evidence is insufficient. | Test reliability versus the number of assessments completed |

Keep the underlying model and test items consistent. Choose combination rules and uncertainty thresholds using validation data, then evaluate once on the held-out test set.

**3. Data needed**

| Resource | Purpose | Status |
|---|---|---|
| **[Freshness44](https://www.kaggle.com/datasets/siavash93/freshness44)** | Candidate public training dataset. | Referenced by the NoisyViT paper. Inspect downloads, labels, licensing, duplicates, and class balance before committing. |
| **Your own multiview photos** | Evaluate different sides of the same physical item. | Must collect unless a suitable paired dataset is found. |
| **Unsuitable-input examples** | Check blurry photos, empty scenes, and unsupported objects. | Must collect for uncertainty evaluation. |
| **Daily observations — extension** | Support remaining-life modeling. | Must collect or find a suitable longitudinal dataset. |

For an initial feasibility pilot, aim for **30–50 distinct physical items with three views each**, spread across available condition labels. This is a planning target, not a guarantee of enough data for the final study.

Record:

- Item ID and produce type.
- Capture date, view ID, and photo filename.
- Condition label and labeling notes.
- Storage conditions and daily observation date if studying remaining life.

Keep **every view and every day of the same item in one split**. Three photos of one apple are three views, not three independent apples. Where public images lack item IDs, inspect for duplicates and disclose that limitation.

**4. Software and hardware**

| Resource | Role |
|---|---|
| **Python and Jupyter** | Data exploration and experiments |
| **PyTorch and torchvision** | Training, image transforms, and inference |
| **timm** | Load a pretrained ConvNeXt V2 model |
| **Pillow; optionally OpenCV** | Image loading and quality checks |
| **scikit-learn** | Metrics, grouped splits, and calibration analysis |
| **pandas and Matplotlib** | Data records, tables, and figures |
| **Streamlit** | Simple upload-and-results interface |
| **CSV files; optionally SQLite** | Local records and assessment history |
| **Overleaf and BibTeX** | Required IEEE paper and references |
| **Git and a locked dependency file** | Preserve code and reproducible settings |

Your previously identified **RTX 4060 laptop GPU with 8 GB VRAM** is a reasonable starting point for a small pretrained model. Confirm batch size and memory use with a short trial.

Physical resources: a phone camera, produce, item labels, a consistent photo location, and storage records. A phone stand is useful but optional. No paid model API is required for this approach.

**5. Model and implementation resources**

- **[ConvNeXt V2 paper — 2023](https://arxiv.org/abs/2301.00808):** modern architecture foundation.
- **[ConvNeXt V2 Atto pretrained model](https://huggingface.co/timm/convnextv2_atto.fcmae_ft_in1k):** small candidate checkpoint. Its listed license is CC BY-NC 4.0; retain attribution and review the terms.
- **[PyTorch transfer-learning tutorial](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html):** adapting pretrained models to a new classification task.
- **[GroupShuffleSplit documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html):** separating data by physical item.
- **[Probability calibration documentation](https://scikit-learn.org/stable/modules/calibration):** assessing whether predicted probabilities reflect observed correctness.
- **[Streamlit camera input](https://docs.streamlit.io/develop/api-reference/widgets/st.camera_input):** capturing images through a browser. File upload is a useful fallback.
- **[Official IEEE conference template on Overleaf](https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn):** report starting point.

**6. Research reading list**

| Source | Why read it |
|---|---|
| **[Fruit and vegetable freshness using deep features and PCA — 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10767316/)** | Understand established freshness-classification methods and datasets. |
| **[Multi-Task NoisyViT — 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12526848/)** | Study joint produce-type and freshness prediction. |
| **[Adaptive knowledge distillation and normalization for fruit freshness — 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12453794/)** | Examine another recent improvement to freshness classification. |
| **[Classifier calibration survey](https://arxiv.org/abs/2112.10327)** | Ground the uncertainty feature in research. |
| **[FDA produce guidance](https://www.fda.gov/food/buy-store-serve-safe-food/selecting-and-serving-produce-safely?linkId=100000002660538)** | Keep application wording consistent with the limits of visual assessment. |

These are starting resources, **not the completed 15-reference bibliography**. Expand the literature review with directly relevant work on multiview fusion, selective prediction, produce datasets, and shelf-life prediction if that extension is included.

**7. Evaluation**

Report:

- Accuracy and macro F1.
- Confusion matrix.
- Visibly spoiled items incorrectly labeled apparently fresh.
- Results by view count.
- Error rate versus the proportion of cases answered.
- Processing time.
- Representative successes and failures.

For remaining-life prediction, additionally report prediction error in days and how often the observed endpoint falls within the predicted range. Do this only if the collected data supports it.

**8. Four-week outline**

| Week | Work and checkpoint |
|---|---|
| **1** | Review research, inspect datasets, choose produce type and labels, begin collection. Confirm that the multiview experiment is feasible. |
| **2** | Train and validate the single-view baseline; implement multiview averaging. |
| **3** | Add uncertainty handling, build the interface, freeze settings, run final evaluation. |
| **4** | Analyze failures, produce figures, finish the paper, document code, and rehearse the presentation. |

If remaining-life prediction stays in scope, begin daily observations in Week 1 and decide early whether there is enough usable data.

**9. Final deliverables**

- Documented source code and environment instructions in a ZIP.
- Saved model, split records, settings, predictions, and evaluation results.
- Data documentation and permitted supporting materials.
- A 4–5 page IEEE paper in LaTeX with at least 15 BibTeX references and editable Overleaf access.
- A 15-minute presentation.
- Preparation to explain the model, data, improvement, results, and limitations in the project exam.

**First decision:** inspect the candidate dataset and choose one produce type. Build the required project around **multiview assessment, visible condition, and uncertainty**, with remaining-life prediction as an extension.
