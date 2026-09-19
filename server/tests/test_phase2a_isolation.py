"""Verify Phase 2A isolation from Agent 2 Commerce Models."""

import subprocess
import sys


def test_customer_commerce_path_has_no_agent2_dependency() -> None:
    """Ensure that importing discovery_service does not import Cart/Order models."""
    script = """
import sys

try:
    from app.modules.commerce import discovery_service
except Exception as e:
    print(f"FAILED_IMPORT: {e}")
    sys.exit(1)

loaded_modules = list(sys.modules.keys())
bad_modules = [
    m for m in loaded_modules
    if "app.modules.commerce.models" in m or "app.modules.inventory.reservation" in m or "app.modules.commerce.cart_service" in m
]

if bad_modules:
    print(f"FAILED_ISOLATION: {bad_modules}")
    sys.exit(1)

print("OK")
sys.exit(0)
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Isolation test failed. Output:\\n{result.stdout}\\n{result.stderr}"
    )
    assert "OK" in result.stdout
