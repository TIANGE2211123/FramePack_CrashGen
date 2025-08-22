# FramePack Training for HunyuanVideo

FramePack is a training technique that allows you to train on longer videos by packing multiple overlapping windows of frames into a single training example. This is particularly useful for training on videos that are longer than what can fit in memory with the standard approach.

## How FramePack Works

1. **Sliding Window**: For a video with N frames and a window size of W, FramePack creates N-W+1 overlapping windows
2. **Packing**: Each window becomes a separate training example, effectively multiplying your training data
3. **Loss Computation**: Loss is computed on each window independently and averaged

## Configuration

To enable FramePack, add these parameters to your model configuration:

```toml
[model]
type = 'hunyuan-video'
framepack = true
framepack_window_size = 33  # Number of frames per window
```

## Example Configuration

Here's a complete example configuration for FramePack training:

```toml
# Main training config
output_dir = '/path/to/output'
dataset = '/path/to/dataset.toml'

epochs = 200
micro_batch_size_per_gpu = 1
gradient_accumulation_steps = 2

[model]
type = 'hunyuan-video'
framepack = true
framepack_window_size = 33

dtype = 'bfloat16'
transformer_dtype = 'float8'
transformer_path = '/path/to/transformer.safetensors'
vae_path = '/path/to/vae.safetensors'
llm_path = '/path/to/text_encoder'
clip_path = '/path/to/clip_encoder'

[adapter]
type = 'lora'
rank = 32
dtype = 'bfloat16'
```

## Dataset Configuration

For FramePack training, you'll want to use longer frame buckets:

```toml
# Dataset config
frame_buckets = [120]  # Videos with 151 frames
resolutions = [[572, 720], [640, 640]]

[[directory]]
path = '/path/to/videos'
num_repeats = 1
```

## Memory Considerations

- FramePack increases memory usage due to the sliding window approach
- Each video creates multiple training examples
- Consider reducing batch size or using gradient accumulation
- The effective batch size becomes `batch_size * num_windows`

## Training Tips

1. **Window Size**: Choose a window size that balances memory usage and temporal context
2. **Frame Buckets**: Use longer frame buckets to take advantage of FramePack
3. **Learning Rate**: You may need to adjust learning rate due to increased effective batch size
4. **Gradient Accumulation**: Use gradient accumulation to maintain stable training

## Example Usage

```bash
NCCL_P2P_DISABLE="1" NCCL_IB_DISABLE="1" deepspeed --num_gpus=1 train.py --deepspeed --config examples/framepack.toml
```

## Limitations

- FramePack is currently only supported for HunyuanVideo
- Requires videos longer than the window size to be effective
- May require more training time due to increased data
- Memory usage scales with window size and number of windows 