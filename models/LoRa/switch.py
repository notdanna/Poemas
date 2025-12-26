#%%
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os
#%%
torch.mps.empty_cache()

device = torch.device("mps")
dtype = torch.float16
BASE_MODEL = "unsloth/Llama-3.2-3B-Instruct"

PATH_ANAFORA = "lora_anafora"
PATH_METAFORA = "modelo_lora_final"
PATH_ALITERACION = "lora_aliteracion"
PATH_PARALELISMO = "lora_paralelismo"
PATH_POLISINDENTON = "lora_polisindeton"
PATH_ASINDENTON = "lora_asindeton"
#%%
print("Tokenizer")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

print("Modelo base directamente en MPS")
# Cargamos directamente en el dispositivo para evitar duplicidad RAM -> MPS
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=dtype,
    device_map={"": "mps"}, # Forzamos el mapa al dispositivo MPS directamente
    trust_remote_code=True
)
#%%
print("LoRA")
try:

    model = PeftModel.from_pretrained(
        model,
        PATH_METAFORA,
        adapter_name="metafora"
    )
    model.load_adapter(PATH_ALITERACION, adapter_name="aliteracion")
    model.load_adapter(PATH_ANAFORA, adapter_name="anafora")
    model.load_adapter(PATH_PARALELISMO, adapter_name="paralelismo")
    model.load_adapter(PATH_POLISINDENTON, adapter_name="polisindeton")
    model.load_adapter(PATH_ASINDENTON, adapter_name="asindenton")

    model.eval()
    print(f"ADAPTADORES: {list(model.peft_config.keys())}")
except Exception as e:
    print(f"Error al cargar adaptadores: {e}")
#%%
def generar_poema(palabra, figura="metafora"):
    model.set_adapter(figura)

    prompt = f'Escribe un poema usando la figura retórica "{figura}" con la palabra "{palabra}".\nPoema:\n'
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=80,      # Reducimos un poco para mayor velocidad
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            use_cache=True          # Crucial para velocidad en inferencia
        )

    resultado = tokenizer.decode(output[0], skip_special_tokens=True)
    poema = resultado.split("Poema:")[-1].strip()

    print(f"\n[{figura.upper()}] {palabra}:\n" + "" + f"\n{poema}\n" + "-"*30)
#%%
if __name__ == "__main__":
    generar_poema("Vida", "aliteracion")
    generar_poema("Vida", "metafora")
    generar_poema("Vida", "anafora")
    generar_poema("Vida", "paralelismo")
    generar_poema("Vida", "polisindeton")
    generar_poema("Vida", "asindenton")