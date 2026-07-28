# TRIDENT job summary

This file is updated once per run and summarizes what TRIDENT has done in this `job_dir`.

- Per-slide machine-readable state lives in `wsi_states/*.json`.
- Per-run manifests live in `runs/*.json`.

## Run 2026-07-21T15:46:21-0500 (trident 0.3.0) — run_id=16076b8c06b5
- Tool: `run_batch_of_slides`
- Status: **completed**
- Finished: `2026-07-21T15:46:27-0500`
- Slides with state: 1
- Args: `{"batch_size": 64, "cache_batch_size": 32, "clear_dead_locks": false, "coords_dir": null, "custom_list_of_wsis": null, "custom_mpp_keys": null, "dead_lock_max_age_hours": 24.0, "device": "cpu", "dump_patches": false, "dump_patches_format": "png", "dump_patches_jpeg_quality": 90, "dump_patches_max": 0, "feat_batch_size": null, "gpu": 0, "job_dir": "/Users/linusliu/trident_lab/base", "mag": 20.0, "max_workers": null, "min_tissue_proportion": 0.0, "overlap": 0, "patch_encoder": "conch_v15", "patch_encoder_ckpt_path": null, "patch_size": 512, "reader_type": null, "remove_artifacts": false, "remove_holes": false, "remove_penmarks": false, "search_nested": false, "seg_batch_size": null, "seg_conf_thresh": 0.5, "segmenter": "otsu", "skip_errors": false, "slide_encoder": null, "task": "seg", "wsi_cache": null, "wsi_dir": "/Users/linusliu/trident_lab/wsis", "wsi_ext": null}`
- segmentation: completed: 1

## Run 2026-07-21T16:10:47-0500 (trident 0.3.0) — run_id=6cd6c20ac006
- Tool: `run_batch_of_slides`
- Status: **completed**
- Finished: `2026-07-21T16:10:47-0500`
- Slides with state: 1
- Args: `{"batch_size": 64, "cache_batch_size": 32, "clear_dead_locks": false, "coords_dir": null, "custom_list_of_wsis": null, "custom_mpp_keys": null, "dead_lock_max_age_hours": 24.0, "device": "cpu", "dump_patches": false, "dump_patches_format": "png", "dump_patches_jpeg_quality": 90, "dump_patches_max": 0, "feat_batch_size": null, "gpu": 0, "job_dir": "/Users/linusliu/trident_lab/base", "mag": 20.0, "max_workers": null, "min_tissue_proportion": 0.0, "overlap": 0, "patch_encoder": "conch_v15", "patch_encoder_ckpt_path": null, "patch_size": 256, "reader_type": null, "remove_artifacts": false, "remove_holes": false, "remove_penmarks": false, "search_nested": false, "seg_batch_size": null, "seg_conf_thresh": 0.5, "segmenter": "hest", "skip_errors": false, "slide_encoder": null, "task": "coords", "wsi_cache": null, "wsi_dir": "/Users/linusliu/trident_lab/wsis", "wsi_ext": null}`
- coords: completed: 1
- segmentation: completed: 1

## Run 2026-07-21T16:26:06-0500 (trident 0.3.0) — run_id=bac8c9617f98
- Tool: `run_batch_of_slides`
- Status: **completed**
- Finished: `2026-07-21T16:26:12-0500`
- Slides with state: 1
- Args: `{"batch_size": 64, "cache_batch_size": 32, "clear_dead_locks": false, "coords_dir": null, "custom_list_of_wsis": null, "custom_mpp_keys": null, "dead_lock_max_age_hours": 24.0, "device": "cpu", "dump_patches": false, "dump_patches_format": "png", "dump_patches_jpeg_quality": 90, "dump_patches_max": 0, "feat_batch_size": null, "gpu": 0, "job_dir": "/Users/linusliu/trident_lab/base", "mag": 20.0, "max_workers": null, "min_tissue_proportion": 0.0, "overlap": 0, "patch_encoder": "resnet50", "patch_encoder_ckpt_path": null, "patch_size": 256, "reader_type": null, "remove_artifacts": false, "remove_holes": false, "remove_penmarks": false, "search_nested": false, "seg_batch_size": null, "seg_conf_thresh": 0.5, "segmenter": "hest", "skip_errors": false, "slide_encoder": null, "task": "feat", "wsi_cache": null, "wsi_dir": "/Users/linusliu/trident_lab/wsis", "wsi_ext": null}`
- coords: completed: 1
- segmentation: completed: 1
- Patch features:
  - resnet50: completed: 1

## Run 2026-07-21T17:18:01-0500 (trident 0.3.0) — run_id=265427a4ee35
- Tool: `run_batch_of_slides`
- Status: **completed**
- Finished: `2026-07-21T17:18:01-0500`
- Slides with state: 1
- Args: `{"batch_size": 64, "cache_batch_size": 32, "clear_dead_locks": false, "coords_dir": null, "custom_list_of_wsis": null, "custom_mpp_keys": null, "dead_lock_max_age_hours": 24.0, "device": "cpu", "dump_patches": false, "dump_patches_format": "png", "dump_patches_jpeg_quality": 90, "dump_patches_max": 0, "feat_batch_size": null, "gpu": 0, "job_dir": "/Users/linusliu/trident_lab/base", "mag": 20.0, "max_workers": null, "min_tissue_proportion": 0.0, "overlap": 0, "patch_encoder": "resnet50", "patch_encoder_ckpt_path": null, "patch_size": 256, "reader_type": null, "remove_artifacts": false, "remove_holes": false, "remove_penmarks": false, "search_nested": false, "seg_batch_size": null, "seg_conf_thresh": 0.5, "segmenter": "hest", "skip_errors": false, "slide_encoder": null, "task": "feat", "wsi_cache": null, "wsi_dir": "/Users/linusliu/trident_lab/wsis", "wsi_ext": null}`
- coords: completed: 1
- segmentation: completed: 1
- Patch features:
  - resnet50: completed: 1

## Run 2026-07-21T17:19:55-0500 (trident 0.3.0) — run_id=0113df58754c
- Tool: `run_batch_of_slides`
- Status: **completed**
- Finished: `2026-07-21T17:19:55-0500`
- Slides with state: 1
- Args: `{"batch_size": 64, "cache_batch_size": 32, "clear_dead_locks": false, "coords_dir": null, "custom_list_of_wsis": null, "custom_mpp_keys": null, "dead_lock_max_age_hours": 24.0, "device": "cpu", "dump_patches": false, "dump_patches_format": "png", "dump_patches_jpeg_quality": 90, "dump_patches_max": 0, "feat_batch_size": null, "gpu": 0, "job_dir": "/Users/linusliu/trident_lab/base", "mag": 20.0, "max_workers": null, "min_tissue_proportion": 0.0, "overlap": 0, "patch_encoder": "resnet50", "patch_encoder_ckpt_path": null, "patch_size": 256, "reader_type": null, "remove_artifacts": false, "remove_holes": false, "remove_penmarks": false, "search_nested": false, "seg_batch_size": null, "seg_conf_thresh": 0.5, "segmenter": "hest", "skip_errors": false, "slide_encoder": null, "task": "feat", "wsi_cache": null, "wsi_dir": "/Users/linusliu/trident_lab/wsis", "wsi_ext": null}`
- coords: completed: 1
- segmentation: completed: 1
- Patch features:
  - resnet50: completed: 1

## Run 2026-07-22T10:56:08-0500 (trident 0.3.0) — run_id=ed8068068868
- Tool: `run_batch_of_slides`
- Status: **completed**
- Finished: `2026-07-22T10:56:08-0500`
- Slides with state: 1
- Args: `{"batch_size": 64, "cache_batch_size": 32, "clear_dead_locks": false, "coords_dir": null, "custom_list_of_wsis": null, "custom_mpp_keys": null, "dead_lock_max_age_hours": 24.0, "device": "cuda:0", "dump_patches": false, "dump_patches_format": "png", "dump_patches_jpeg_quality": 90, "dump_patches_max": 0, "feat_batch_size": null, "gpu": 0, "job_dir": "/Users/linusliu/trident_lab/base", "mag": 20.0, "max_workers": null, "min_tissue_proportion": 0.0, "overlap": 0, "patch_encoder": "conch_v15", "patch_encoder_ckpt_path": null, "patch_size": 512, "reader_type": null, "remove_artifacts": false, "remove_holes": false, "remove_penmarks": false, "search_nested": false, "seg_batch_size": null, "seg_conf_thresh": 0.5, "segmenter": "hest", "skip_errors": false, "slide_encoder": null, "task": "seg", "wsi_cache": null, "wsi_dir": "/Users/linusliu/trident_lab/wsis", "wsi_ext": null}`
- coords: completed: 1
- segmentation: completed: 1
- Patch features:
  - resnet50: completed: 1
