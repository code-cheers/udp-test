# udp-test

基于 Mininet 的 TCP/UDP 丢包测试脚手架。只保留“丢包率 1% → 3% → 6%”场景，用于对比 UDP/TCP 的 P99 RTT 差异（无额外延迟、无乱序）。

## 依赖

- Docker（需要特权容器，宿主机需可用 `/lib/modules`）

## 运行（Docker）

丢包扫档位（1%/3%/6%）并输出图表：

```sh
make docker-loss-sweep COUNT=200 INTERVAL_MS=16
```

输出图表：`plots/loss_sweep_p99.png`

自定义丢包档位：

```sh
make docker-loss-sweep LOSS_LEVELS="1 3 6 10" COUNT=200 INTERVAL_MS=16
```

## 文件说明

- `scripts/mn_latency.py`: 构建 2-host Mininet 拓扑并运行 TCP/UDP 探测
- `scripts/udp_echo_server.py`: UDP 回显服务端
- `scripts/udp_echo_client.py`: UDP RTT 探测客户端
- `scripts/tcp_echo_server.py`: TCP 回显服务端
- `scripts/tcp_echo_client.py`: TCP RTT 探测客户端
- `scripts/loss_sweep_plot.py`: 丢包扫档位并生成 P99 图
