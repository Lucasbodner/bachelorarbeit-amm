from llama_cpp import Llama

def load_local_model():
    return Llama(
        model_path="model/Llama-3.2-1B-merged-lora-q4_k.gguf",
        n_ctx=2048,
        n_gpu_layers=-1,  # ❌ force à ne PAS utiliser le GPU
        use_mlock=False,  # ✅ évite les conflits mémoire Metal
        use_mmap=True
    )


def generate_response(llm, prompt, max_tokens=200):
    output = llm(prompt, max_tokens=max_tokens)
    return output["choices"][0]["text"].strip()
