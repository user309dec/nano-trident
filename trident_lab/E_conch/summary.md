# TRIDENT job summary

This file is updated once per run and summarizes what TRIDENT has done in this `job_dir`.

- Per-slide machine-readable state lives in `wsi_states/*.json`.
- Per-run manifests live in `runs/*.json`.

## Run 2026-07-21T17:26:59-0500 (trident 0.3.0) — run_id=fc7dc5c534ea
- Tool: `run_batch_of_slides`
- Status: **completed**
- Finished: `2026-07-21T17:33:27-0500`
- Slides with state: 1
- Args: `{"batch_size": 64, "cache_batch_size": 32, "clear_dead_locks": false, "coords_dir": null, "custom_list_of_wsis": null, "custom_mpp_keys": null, "dead_lock_max_age_hours": 24.0, "device": "cpu", "dump_patches": false, "dump_patches_format": "png", "dump_patches_jpeg_quality": 90, "dump_patches_max": 0, "feat_batch_size": null, "gpu": 0, "job_dir": "/Users/linusliu/trident_lab/E_conch", "mag": 20.0, "max_workers": null, "min_tissue_proportion": 0.0, "overlap": 0, "patch_encoder": "conch_v15", "patch_encoder_ckpt_path": null, "patch_size": 512, "reader_type": null, "remove_artifacts": false, "remove_holes": false, "remove_penmarks": false, "search_nested": false, "seg_batch_size": null, "seg_conf_thresh": 0.5, "segmenter": "otsu", "skip_errors": false, "slide_encoder": null, "task": "all", "wsi_cache": null, "wsi_dir": "/Users/linusliu/trident_lab/wsis", "wsi_ext": null}`
- coords: completed: 1
- segmentation: completed: 1
- Patch features:
  - conch_v15: completed: 1

## Run 2026-07-21T17:38:08-0500 (trident 0.3.0) — run_id=ebc6c41dd4e9
- Tool: `run_batch_of_slides`
- Status: **completed**
- Finished: `2026-07-21T17:38:08-0500`
- Slides with state: 1
- Args: `{"batch_size": 64, "cache_batch_size": 32, "clear_dead_locks": false, "coords_dir": null, "custom_list_of_wsis": null, "custom_mpp_keys": null, "dead_lock_max_age_hours": 24.0, "device": "cpu", "dump_patches": false, "dump_patches_format": "png", "dump_patches_jpeg_quality": 90, "dump_patches_max": 0, "feat_batch_size": null, "gpu": 0, "job_dir": "/Users/linusliu/trident_lab/E_conch", "mag": 20.0, "max_workers": null, "min_tissue_proportion": 0.0, "overlap": 0, "patch_encoder": "conch_v15", "patch_encoder_ckpt_path": null, "patch_size": 512, "reader_type": null, "remove_artifacts": false, "remove_holes": false, "remove_penmarks": false, "search_nested": false, "seg_batch_size": null, "seg_conf_thresh": 0.5, "segmenter": "otsu", "skip_errors": false, "slide_encoder": null, "task": "all", "wsi_cache": null, "wsi_dir": "/Users/linusliu/trident_lab/wsis", "wsi_ext": null}`
- coords: completed: 1
- segmentation: completed: 1
- Patch features:
  - conch_v15: completed: 1
