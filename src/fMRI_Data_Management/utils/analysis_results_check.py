import yaml
import os
import glob
import pandas as pd

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

def safe_glob(pattern):
    return glob.glob(pattern, recursive=True)

def count_check(base_dir, subject, session, rule):
    results = []
    for dt, spec in rule.get("data_types", {}).items():
        pattern = spec["pattern"]
        expected = spec.get("expected_count", 0)
        tol = spec.get("tolerance", 0)
        files = safe_glob(os.path.join(base_dir, pattern))
        cnt = len(files)
        diff = cnt - expected
        status = "PASS" if abs(diff) <= tol else f"EXCEEDS_EXPECTATION_ON_{dt}" if diff > tol else f"FAIL_ON_{dt}"
        results.append({
            "task": "recon_bids",
            "subject": subject,
            "session": session,
            "data_type": dt,
            "pattern": pattern,
            "expected_count": expected,
            "actual_count": cnt,
            "tolerance": tol,
            "status": status,
            "extra_files": cnt - expected if cnt > expected else 0
        })
    return results

def required_files_check(task, path, files, subject, session):
    results = []
    for f in files:
        exists = bool(safe_glob(os.path.join(path, f)))
        results.append({
            "task": task,
            "subject": subject,
            "session": session,
            "pattern": f,
            "actual_count": 1 if exists else 0,
            "status": "PASS" if exists else f"FAIL_ON_{f}"
        })
    return results

def perform_checks(config, work_dir, subject, session, prefix=""):
    all_results = []
    for task, conf in config.items():
        path = conf["output_path"].format(work_dir=work_dir, subject=subject, session=session, prefix=prefix)
        if "raw_count_check" in conf and conf["raw_count_check"].get("enabled", False):
            all_results.extend(count_check(path, subject, session, conf["raw_count_check"]))
        if "required_files" in conf:
            all_results.extend(required_files_check(task, path, conf["required_files"], subject, session))
    return pd.DataFrame(all_results)

if __name__ == "__main__":
    CONFIG_PATH = r"src/fMRI_Data_Management/config/task_output_checks.yaml"
    WORK_DIR = r"/data/processed"
    SUBJECT = "001"
    SESSION = "01"
    PREFIX = "sub-"

    cfg = load_config(CONFIG_PATH)
    df = perform_checks(cfg, WORK_DIR, SUBJECT, SESSION, PREFIX)
    print(df)
    df.to_csv("check_results.csv", index=False)
