from mininet.net import Mininet
from mininet.link import TCLink
from mininet.topo import Topo
from sshd import sshd
from mininet.log import lg, info
import sys
import argparse

# <<< 修改部分 (1): 更新网络配置以支持4个节点
NETWORK_CONFIG = {
    "link": TCLink,
    "hosts": ['h1', 'h2', 'h3', 'h4'],  # 添加 h4
    "bw": [1000, 1000, 1000, 1000],   # 为 h4 添加带宽
    "delay": ['1us', '1us', '1us', '1us'], # 为 h4 添加延迟
    "ips": ['10.0.0.11', '10.0.0.12', '10.0.0.13', '10.0.0.14'] # 为 h4 分配新IP
}

class RoundRoleNet( Topo ):

    def __init__(self, *args, **params):
        Topo.__init__(self, *args, **params)

    def build( self ):
        self.hosts_list = []
        self.switches_list = []
        # 注意：这里的 self.network_config 会在运行时被主程序的 NETWORK_CONFIG 覆盖
        # 但为了清晰，我们让它直接使用全局配置
        self.network_config = NETWORK_CONFIG

        self.switches_list.append(self.addSwitch(name='s1', stp=True, failMode='standalone'))

        # 这部分代码无需修改，因为它会根据 `len(self.network_config['hosts'])` 自动调整
        hosts_num = len(self.network_config['hosts'])
        for i in range(hosts_num):
            h = self.addHost(name=self.network_config['hosts'][i], ip=self.network_config['ips'][i])
            self.hosts_list.append(h)

        # 这部分代码也无需修改，它会为所有主机创建到交换机的链接
        for i in range(hosts_num):
            self.addLink(self.hosts_list[i], self.switches_list[0], bw=self.network_config['bw'][i], delay=self.network_config['delay'][i], use_hfsc=True)

        return

def get_mininet(topo):
    return Mininet(topo, waitConnected=True, link=TCLink)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, help='the ip address of the host pod')
    # <<< 修改部分 (2): 更新命令行参数的默认值
    parser.add_argument('--bw', type=int, nargs='+', help='bandwidthes of each host', default=NETWORK_CONFIG['bw'])
    args = parser.parse_args()

    # 如果用户通过命令行提供了 --bw 参数，这里会覆盖 NETWORK_CONFIG['bw'] 的值
    # 如果用户提供了4个值，例如 --bw 100 200 300 400，它会正常工作
    NETWORK_CONFIG['bw'] = args.bw

    lg.setLogLevel('info')
    topo = RoundRoleNet()
    net = get_mininet(topo)
    argvopts = '-D -o UseDNS=no -u0'

    print("argvopts: ", argvopts)
    # 确保sshd脚本存在于同一目录或Python路径中
    # 假设 sshd.py 是您已有的辅助文件
    try:
        sshd(net, opts=argvopts, routes=['10.222.0.0/24'], ip=args.ip)
    except NameError:
        print("错误: sshd 函数未定义。")
        print("请确保您有一个名为 sshd.py 的文件，其中包含 sshd 函数，并与此脚本放在同一目录中。")
        net.stop()