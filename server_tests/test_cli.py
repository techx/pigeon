from click.testing import Result


def test_seed_corpus(runner):
    result: Result = runner.invoke(args=["seed", "corpus"])
    print(result.stdout)
    assert result.exit_code == 0

def test_seed_email(runner):
    result: Result = runner.invoke(args=["seed", "email"])
    print(result.stdout)
    assert result.exit_code == 0

def test_seed_thread(runner):
    result: Result = runner.invoke(args=["seed", "thread"])
    print(result.stdout)
    assert result.exit_code == 0
