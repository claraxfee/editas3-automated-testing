python3 -m vllm.entrypoints.openai.api_server \
	--model Qwen/Qwen3-Coder-30B-A3B-Instruct \
	--tensor-parallel-size 4 \
	--gpu-memory-utilization 0.95

#--max_model_len 20480 \
#--dtype bfloat16
#--model Qwen/Qwen1.5-72B \
#--model deepseek-ai/DeepSeek-V3 \
#--model Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8 \
#--enable-expert-parallel \
#--model Qwen/Qwen1.5-7B \
