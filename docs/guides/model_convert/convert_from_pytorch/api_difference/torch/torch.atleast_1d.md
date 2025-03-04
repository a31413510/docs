## [ 输入参数用法不一致 ]torch.atleast_1d

### [torch.atleast_1d](https://pytorch.org/docs/stable/generated/torch.atleast_1d.html#torch-atleast-1d)

```python
torch.atleast_1d(*tensors)
```

### [paddle.atleast_1d](https://www.paddlepaddle.org.cn/documentation/docs/zh/develop/api/paddle/atleast_1d_cn.html#atleast_1d)

```python
paddle.atleast_1d(*inputs, name=None)
```

PyTorch 与 Paddle 参数不一致，具体如下：

### 参数映射

| PyTorch       | PaddlePaddle | 备注                                                   |
| ------------- | ------------ | ------------------------------------------------------ |
| <font color='red'> tensors </font> | <font color='red'> inputs </font> | 输入的 Tensor，仅当 torch 输入为 tuple(Tensor)时，两者处理方式不一致，需要转写。其他情形下均一致。 |

PyTorch 与 Paddle 功能一致，但对于由多个 Tensor 组成 tuple|list 输入的处理方式略有不同，具体请看转写示例。

### 转写示例

#### tensors: 输入为 tuple(Tensor)时

```python
# PyTorch 写法
torch.atleast_1d((x, y))

# Paddle 写法
paddle.atleast_1d(x, y)
```
