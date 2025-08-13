

export HF_HOME=/data1/huggingface_cache
export CUDA_DEVICE_ORDER=PCI_BUS_ID




vllm serve \
	deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
	--tensor_parallel_size 4 \
	--gpu_memory_utilization=0.95 \
	--max_model_len 13000 

#Qwen/Qwen3-Coder-30B-A3B-Instruct \
#deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct \
#deepseek-ai/DeepSeek-R1-0528-Qwen3-8b \
#Qwen/Qwen2.5-Coder-32B-Instruct \
