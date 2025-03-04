## [torch 参数更多]torch.Tensor.new_ones

### [torch.Tensor.new_ones](https://pytorch.org/docs/stable/generated/torch.Tensor.new_ones.html#torch-tensor-new-ones)

```python
torch.Tensor.new_ones(*size, *, dtype=None, device=None, requires_grad=False, layout=torch.strided, pin_memory=False)
```

### [paddle.ones](https://www.paddlepaddle.org.cn/documentation/docs/zh/develop/api/paddle/ones_cn.html)

```python
paddle.ones(shape,
             dtype=None,
             name=None)
```

PyTorch 相比 Paddle 支持更多其他参数，具体如下：

### 参数映射

| PyTorch       | PaddlePaddle | 备注                                                         |
| ------------- | ------------ | ------------------------------------------------------------ |
| *size         | shape        | 表示输出形状大小， PyTorch 是可变参数用法， Paddle 是列表或元组，需要转写。 |
| dtype         | dtype        | 表示输出 Tensor 类型，如果没有指定，默认使用当前对象的 dtype，需要转写。    |
| device        | -            | 表示 Tensor 存放设备位置，Paddle 无此参数，需要转写。    |
| requires_grad | -            | 表示是否计算梯度，Paddle 无此参数，需要转写。            |
| layout        | -            | 表示布局方式，Paddle 无此参数，一般对网络训练结果影响不大，可直接删除。 |
| pin_memory    | -            | 表示是否使用锁页内存， Paddle 无此参数，需要转写。       |

### 转写示例

#### size：输出形状大小

```python
# PyTorch 写法
x.new_ones(3, 5)

# Paddle 写法
paddle.ones([3, 5])
```

#### dtype：数据类型

```python
# PyTorch 写法
x.new_ones(3, 5)

# Paddle 写法
paddle.ones([3, 5], dtype=x.dtype)
```


#### device: Tensor torch 的设备

```python
# PyTorch 写法
y = x.new_ones((3, 5), device=torch.device('cpu'))

# Paddle 写法
y = paddle.ones([3, 5])
y.cpu()
```

#### requires_grad：是否求梯度

```python
# PyTorch 写法
y = x.new_ones((3, 5), requires_grad=True)

# Paddle 写法
y = paddle.ones([3, 5])
y.stop_gradient = False
```

#### pin_memory：是否分配到固定内存上

```python
# PyTorch 写法
y = x.new_ones((3, 5), pin_memory=True)

# Paddle 写法
y = paddle.ones([3, 5]).pin_memory()
```
