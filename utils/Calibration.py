import json
from pathlib import Path

def calibrate_metrics(cta: dict, cta2vta: dict, pfx: str) -> dict:
    """
    Multiply metrics by the slope from Calibrations.json.

    Parameters:
        cta (dict): Original metrics (weighted or unweighted)
        cta2vta (dict): Calibration slopes
        pfx (str): Prefix to match calibration keys, e.g., 'CTA.SaliencyWtdMean_' or 'CTA.Global_'

    Returns:
        dict: New dict with calibrated metrics prefixed with 'Calibrated'
    """
    def strip(metric):
        return metric.replace('Mean_', '').replace('Std_', '')

    return {
        f"Cal{metric}": val * cta2vta[f"{pfx}{strip(metric)}"]["slope"]
        for metric, val in cta.items()
        if f"{pfx}{strip(metric)}" in cta2vta
    }


def calibrate_slide_metrics(metrics_path: str, calibrations_path: str, output_path: str) -> None:
    """
    Apply calibrations to slide-level metrics JSON.

    Parameters:
        metrics_path (str): Path to exported metrics JSON (results.json)
        calibrations_path (str): Path to Calibrations.json
        output_path (str): Path to save calibrated JSON
    """
    # Load original metrics
    with open(metrics_path, 'r') as f:
        data = json.load(f)

    # Load calibration slopes
    with open(calibrations_path, 'r') as f:
        cta2vta = json.load(f)

    # Calibrate weighted metrics
    weighted = data['metrics'].get('weighted_by_rois', {})
    weighted_cal = calibrate_metrics(weighted, cta2vta, pfx='CTA.SaliencyWtdMean_')
    data['metrics']['weighted_by_rois'].update(weighted_cal)

    # Calibrate unweighted metrics
    unweighted = data['metrics'].get('unweighted_global', {})
    unweighted_cal = calibrate_metrics(unweighted, cta2vta, pfx='CTA.Global_')
    data['metrics']['unweighted_global'].update(unweighted_cal)

    # Save calibrated JSON
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Calibrated metrics saved to: {output_path}")

if __name__ == "__main__":

    calibrations_json_path = "./Calibration.json"
    metrics_json_path = input("Enter the path to the directory containing metrics JSON files: ")

    results_files = list(Path(metrics_json_path).rglob("*.json"))
    results_files = [f for f in results_files if "roiMeta" not in str(f.parent)]

    for results_file in results_files:
        print(f"Processing file: {results_file}")

        output_file = results_file.with_name(results_file.stem + "_calibrated.json")

        calibrate_slide_metrics(
            metrics_path=str(results_file),
            calibrations_path=calibrations_json_path,
            output_path=str(output_file)
        )