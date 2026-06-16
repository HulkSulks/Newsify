import csv
import datetime

_history = []

def add_entry(source_type, text_preview, result_label, confidence):
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_type": source_type, # "URL" or "Image"
        "preview": text_preview[:50] + "...",
        "result": result_label,
        "confidence": f"{confidence * 100:.2f}%"
    }
    _history.append(entry)

def get_history():
    return _history

def export_to_csv(filepath="fake_news_history.csv"):
    if not _history:
        return False
    keys = _history[0].keys()
    with open(filepath, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(_history)
    return True
