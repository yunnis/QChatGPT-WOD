class RootState:
    def __init__(self):
        self.state = 256

    def state_open(self, position):
        self.state |= (1 << position)  # 打开指定开关

    def state_close(self, position):
        self.state &= ~(1 << position)  # 关闭指定开关

    def state_toggle(self, position):
        self.state ^= (1 << position)  # 切换指定开关的状态

    def state_check(self, position):
        return (self.state & (1 << position)) != 0  # 检查指定开关状态