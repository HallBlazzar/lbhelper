from lbhelper.targets import Target
from lbhelper.target_writer import TargetHandler, TargetWriter


class MockedTarget(Target):
    pass


class MockedTargetHandler(TargetHandler):
    def __init__(self):
        self.received_target = None
    def execute(self, targets):
        self.received_target = targets

def test_target_writer():
    handler = MockedTargetHandler()

    TargetWriter(
        target_handlers={
            MockedTarget: handler.execute
        },
        targets=[MockedTarget() for _ in range(3)]
    ).execute()

    assert len(handler.received_target) == 3
