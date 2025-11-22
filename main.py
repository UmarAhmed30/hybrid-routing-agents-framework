from vllm import LLM, SamplingParams

llm = LLM(
    'facebook/opt-125m',
    gpu_memory_utilization=0.5,
    enforce_eager=True
)
params = SamplingParams(max_tokens=128, temperature=0.7)

outputs = llm.generate(['What is 2+2?'], params)

print(outputs[0].outputs[0].text.strip())

#def main():
#    print("Hello from hybrid-routing-agents-framework!")


#if __name__ == "__main__":
#    main()
