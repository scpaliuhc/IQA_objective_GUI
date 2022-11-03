import pickle
import json

with open('breakpoint', 'rb') as f:
    bp = pickle.load(f)
    f.close()
global_dic, current_ref, current_ae, root_path = bp
global_dic['current_ref'] = current_ref
global_dic['current_ae'] = current_ae
global_dic['root_path'] = root_path

with open('breakpoint.json', 'w') as f:
    json.dump(global_dic, f, indent=4, ensure_ascii=False)