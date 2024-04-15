from click.testing import Result


def test_seed_email(runner):
    result: Result = runner.invoke(args=["seed", "email"])
    print(result.stdout)
    assert result.exit_code == 0
