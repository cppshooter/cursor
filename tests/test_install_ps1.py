import os
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / "install.ps1"


def read_installer() -> str:
    assert INSTALLER.exists(), "install.ps1 should exist for Windows users"
    return INSTALLER.read_text(encoding="utf-8")


def test_windows_installer_supports_same_platforms_as_shell_installer():
    content = read_installer()

    expected_platform_paths = {
        "claude-code": ".claude\\skills",
        "hermes": ".hermes\\skills",
        "openclaw": ".openclaw\\skills",
        "deepseek-tui": ".deepseek\\skills",
    }

    for platform, path_fragment in expected_platform_paths.items():
        assert platform in content
        assert path_fragment in content


def test_windows_installer_sets_bid_skill_home_for_session_and_user():
    content = read_installer()

    assert "$env:BID_SKILL_HOME = $Dest" in content
    assert "[Environment]::SetEnvironmentVariable(" in content
    assert "'BID_SKILL_HOME'" in content
    assert "'User'" in content


def test_windows_installer_keeps_shell_installer_safety_guard():
    content = read_installer()

    assert "[string]::IsNullOrWhiteSpace($Dest)" in content
    assert "$Dest -eq [System.IO.Path]::GetPathRoot($Dest)" in content
    assert "$Dest -notlike '*awesome-bid*'" in content


def test_windows_installer_copies_only_runtime_files():
    content = read_installer()

    for item in [
        "SKILL.md",
        "agents",
        "skills",
        "knowledge",
        "memory",
        "templates",
        "tools",
    ]:
        assert item in content

    assert "install.sh" not in content
    assert ".git" not in content


def test_windows_installer_validates_sources_before_removing_existing_install():
    content = read_installer()

    preflight_position = content.index("# 校验安装源完整性")
    remove_position = content.index("Remove-Item -LiteralPath $Dest")

    assert preflight_position < remove_position


def test_windows_installer_runs_in_isolated_home_when_pwsh_available():
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        return

    with tempfile.TemporaryDirectory() as temp_home:
        env = os.environ.copy()
        env["HOME"] = temp_home
        env["USERPROFILE"] = temp_home

        result = subprocess.run(
            [
                pwsh,
                "-NoProfile",
                "-NonInteractive",
                "-File",
                str(INSTALLER),
                "claude-code",
            ],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        assert result.returncode == 0, result.stdout + result.stderr

        dest = Path(temp_home) / ".claude" / "skills" / "awesome-bid"
        for item in [
            "SKILL.md",
            "agents",
            "skills",
            "knowledge",
            "memory",
            "templates",
            "tools",
        ]:
            assert (dest / item).exists()


if __name__ == "__main__":
    test_windows_installer_supports_same_platforms_as_shell_installer()
    test_windows_installer_sets_bid_skill_home_for_session_and_user()
    test_windows_installer_keeps_shell_installer_safety_guard()
    test_windows_installer_copies_only_runtime_files()
    test_windows_installer_validates_sources_before_removing_existing_install()
    test_windows_installer_runs_in_isolated_home_when_pwsh_available()
