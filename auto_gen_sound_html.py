import os
import asyncio
import edge_tts
import pandas as pd
import re
import json
import uuid
from tqdm.asyncio import tqdm_asyncio
from asyncio import Semaphore
from pydub import AudioSegment

# --- CẤU HÌNH ---
FILE_EXCEL = "data.xlsx"
OUTPUT_FOLDER = "TestHD_Sounds"
TEMP_FOLDER = "Temp_Audio"
FILE_JS_OUTPUT = "ScenarioData.js" 
FILE_JSON_OUTPUT = "dictionary.json"
FILE_HISTORY = "history_log.json"
SHEET_CONFIG_ERRORS = "Config_Errors"
SHEET_LESSON_NAMES = "ten_bai"

CONCURRENT_LIMIT = 5
MAX_RETRIES = 3
RETRY_DELAY = 2
TTS_RATE = "-10%"
TTS_VOLUME = "+0%"

VOICES = {
    "vi_female": "vi-VN-HoaiMyNeural",
    "vi_male":   "vi-VN-NamMinhNeural",
    "ru_female": "ru-RU-SvetlanaNeural",
    "ru_male":   "ru-RU-DmitryNeural"
}

failed_files = []

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_")

def is_russian(text):
    return bool(re.search(r'[А-Яа-яЁё]', text))

def merge_audio_files(temp_files, output_path):
    try:
        combined = AudioSegment.empty()
        for f in temp_files:
            if os.path.exists(f) and os.path.getsize(f) > 0:
                audio = AudioSegment.from_file(f)
                combined += audio
        
        parent_dir = os.path.dirname(output_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            
        combined.export(output_path, format="mp3")
    except Exception as e:
        print(f"\n❌ Lỗi khi ghép file {output_path}: {e}")
    finally:
        for f in temp_files:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass

async def generate_single_tts(text, voice, file_path):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=TTS_RATE, volume=TTS_VOLUME)
            await communicate.save(file_path)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 100:
                return True
        except Exception as e:
            if attempt < MAX_RETRIES: await asyncio.sleep(RETRY_DELAY)
    return False

async def generate_mixed_audio_task(text, vi_voice, ru_voice, file_path, sem):
    async with sem:
        if not text or str(text).lower() == "nan": return
        
        chunks = re.split(r'([А-Яа-яЁё]+(?:[\s\-\_]+[А-Яа-яЁё]+)*)', text)
        chunks = [c for c in chunks if c.strip()]
        
        temp_files = []
        success = True
        
        for i, chunk in enumerate(chunks):
            if not re.search(r'[a-zA-Z0-9À-ỹА-Яа-яЁё]', chunk):
                continue
                
            temp_file = os.path.join(TEMP_FOLDER, f"temp_{uuid.uuid4().hex}_{i}.mp3")
            voice_to_use = ru_voice if is_russian(chunk) else vi_voice
            
            res = await generate_single_tts(chunk, voice_to_use, temp_file)
            if res:
                temp_files.append(temp_file)
            else:
                success = False
                failed_files.append(f"{os.path.basename(file_path)} | Lỗi đoạn: {chunk}")
                break
        
        if success and temp_files:
            await asyncio.to_thread(merge_audio_files, temp_files, file_path)

async def main():
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(TEMP_FOLDER): os.makedirs(TEMP_FOLDER)
    if not os.path.exists(FILE_EXCEL): print(f"❌ Lỗi: Không thấy file {FILE_EXCEL}"); return

    sem = Semaphore(CONCURRENT_LIMIT)
    tasks = []
    
    old_history = {}
    if os.path.exists(FILE_HISTORY):
        try:
            with open(FILE_HISTORY, "r", encoding="utf-8") as f: old_history = json.load(f)
        except: old_history = {}
    new_history = {}

    print(f"--- 📊 ĐANG PHÂN TÍCH EXCEL ---")
    try:
        xls = pd.ExcelFile(FILE_EXCEL)
        all_sheets = pd.read_excel(xls, sheet_name=None, header=None, dtype=str)
        all_sheet_names_ordered = xls.sheet_names
    except Exception as e: print(f"❌ Lỗi đọc Excel: {e}"); return

    list_steps_for_flash = []
    list_errors_for_flash = []
    web_dictionary = {}

    if SHEET_CONFIG_ERRORS in all_sheets:
        print(f"⚙️ Xử lý sheet lỗi: {SHEET_CONFIG_ERRORS}")
        df_err = all_sheets[SHEET_CONFIG_ERRORS]
        sys_path = os.path.join(OUTPUT_FOLDER, "System_Sounds")
        if not os.path.exists(sys_path): os.makedirs(sys_path)
        
        error_count = 0
        for index, row in df_err.iterrows():
            if index == 0: continue
            try:
                txt_vi = str(row[1]).strip()
                txt_ru = str(row[2]).strip()
            except: continue
            if txt_vi.lower() == "nan" or not txt_vi: continue

            error_count += 1
            list_errors_for_flash.append(f"{txt_vi} | {txt_ru}")

            def create_err_audio(txt, vi_v, ru_v, lang, gender, idx):
                fname = f"error_{lang}_{gender}_{idx}.mp3"
                fpath = os.path.join(sys_path, fname)
                key = f"System/{fname}"
                h = f"{txt}_{TTS_RATE}"
                new_history[key] = h
                if not os.path.exists(fpath) or key not in old_history or old_history[key] != h:
                    tasks.append(generate_mixed_audio_task(txt, vi_v, ru_v, fpath, sem))

            create_err_audio(txt_vi, VOICES["vi_female"], VOICES["ru_female"], "vi", "female", error_count)
            create_err_audio(txt_vi, VOICES["vi_male"],   VOICES["ru_male"],   "vi", "male",   error_count)
            create_err_audio(txt_ru, VOICES["ru_female"], VOICES["ru_female"], "ru", "female", error_count)
            create_err_audio(txt_ru, VOICES["ru_male"],   VOICES["ru_male"],   "ru", "male",   error_count)

    for sheet_name in all_sheet_names_ordered:
        if sheet_name in [SHEET_CONFIG_ERRORS, SHEET_LESSON_NAMES]: continue
        if sheet_name not in all_sheets: continue

        df = all_sheets[sheet_name]
        clean_sheet_name = sanitize_filename(sheet_name)
        base_sheet_path = os.path.join(OUTPUT_FOLDER, clean_sheet_name)
        path_vi = os.path.join(base_sheet_path, "VI"); 
        if not os.path.exists(path_vi): os.makedirs(path_vi, exist_ok=True)
        path_ru = os.path.join(base_sheet_path, "RU"); 
        if not os.path.exists(path_ru): os.makedirs(path_ru, exist_ok=True)

        for index, row in df.iterrows():
            try:
                val = str(row[1]).lower()
                if "tên nút" in val or "mc cấp" in val or val == "nan": continue
                
                cols = [str(row[i]).strip() for i in range(1, 10)]
                mc1, mc2, mc3, mc4, mc5, phan, buoc, t_vi, t_ru = cols

                parts = []
                for p in [mc1, mc2, mc3, mc4, mc5, phan, buoc]:
                    if p and p.lower() != 'nan':
                        parts.append(p)
                
                full_id = ".".join(parts)
                full_us = f"{sheet_name}_{full_id.replace('.', '_')}"

                list_steps_for_flash.append(f"{sheet_name} | {full_id} | {t_vi} | {t_ru}")

                if full_id and t_vi and t_vi.lower() != "nan":
                    web_dictionary[full_id] = t_vi

                def proc_dl(txt, primary_voice, secondary_voice, suf, fldr, lc):
                    if txt and txt != "nan":
                        fname = sanitize_filename(f"{full_us}_{suf}.mp3")
                        fp = os.path.join(fldr, fname)
                        key = f"{clean_sheet_name}/{lc}/{fname}"
                        h = f"{txt}_{TTS_RATE}"
                        new_history[key] = h
                        if not os.path.exists(fp) or key not in old_history or old_history[key] != h:
                            tasks.append(generate_mixed_audio_task(txt, primary_voice, secondary_voice, fp, sem))

                proc_dl(t_vi, VOICES["vi_female"], VOICES["ru_female"], "vi_female", path_vi, "VI")
                proc_dl(t_vi, VOICES["vi_male"],   VOICES["ru_male"],   "vi_male",   path_vi, "VI")
                proc_dl(t_ru, VOICES["ru_female"], VOICES["ru_female"], "ru_female", path_ru, "RU")
                proc_dl(t_ru, VOICES["ru_male"],   VOICES["ru_male"],   "ru_male",   path_ru, "RU")
            except: continue

    if len(tasks) > 0:
        print(f"🚀 Đang xử lý {len(tasks)} file âm thanh ghép đa ngôn ngữ...")
        await tqdm_asyncio.gather(*tasks)
    else:
        print("✅ Tất cả file âm thanh đã tồn tại (Skip download).")
    
    if len(failed_files) < 5:
        with open(FILE_HISTORY, "w", encoding="utf-8") as f: json.dump(new_history, f, indent=4)
        
    if os.path.exists(TEMP_FOLDER) and not os.listdir(TEMP_FOLDER):
        os.rmdir(TEMP_FOLDER)

    print(f"📝 Đang tạo file {FILE_JS_OUTPUT}...")
    lesson_name_map = {}
    
    scenario_sheets = [s for s in all_sheet_names_ordered if s not in [SHEET_CONFIG_ERRORS, SHEET_LESSON_NAMES]]
    
    if SHEET_LESSON_NAMES in all_sheets:
        df_names = all_sheets[SHEET_LESSON_NAMES]
        for index, row in df_names.iterrows():
            if index == 0: continue
            try:
                scenario_idx = index - 1
                if scenario_idx < len(scenario_sheets):
                    lesson_name_map[scenario_sheets[scenario_idx]] = str(row[1]).strip()
            except: pass

    with open(FILE_JS_OUTPUT, "w", encoding="utf-8") as f:
        # CỐT LÕI: Gắn trực tiếp vào window để thành biến toàn cục (Global Variable)
        f.write('window.ScenarioData = {\n')
        f.write('\trawData: "",\n')
        f.write('\trawErrors: "",\n')
        f.write('\tlessonNames: ' + json.dumps(lesson_name_map, ensure_ascii=False, indent=4) + ',\n\n')
        
        f.write('\tinitData: function() {\n')
        
        for line in list_steps_for_flash:
            clean_line = line.replace("\"", "\\\"").replace("\n", "")
            f.write(f'\t\tthis.rawData += "{clean_line}\\n";\n')
        
        f.write('\n')
        
        for line in list_errors_for_flash:
            clean_line = line.replace("\"", "\\\"").replace("\n", "")
            f.write(f'\t\tthis.rawErrors += "{clean_line}\\n";\n')
            
        f.write('\t}\n};\n')
        f.write('window.ScenarioData.initData();\n')
        # Lược bỏ đoạn gán vào exportRoot vì đoạn script nạp dữ liệu động của đồng chí đã làm việc này.

    print(f"🌍 Đang tạo file từ điển: {FILE_JSON_OUTPUT}...")
    with open(FILE_JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(web_dictionary, f, ensure_ascii=False, indent=4)

    print(f"\n✅ XONG! Đã tạo '{FILE_JS_OUTPUT}' và '{FILE_JSON_OUTPUT}'.")

if __name__ == "__main__":
    asyncio.run(main())