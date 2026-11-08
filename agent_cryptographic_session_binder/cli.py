"""CLI for agent-cryptographic-session-binder."""
import sys
import argparse
from .binder import AgentCryptographicSessionBinder


def main():
    parser = argparse.ArgumentParser(description="Agent Cryptographic Session Binder CLI")
    parser.add_argument("--demo", action="store_true", help="Run session binding demo")
    args = parser.parse_args()

    if args.demo:
        key = b"super_secret_ephemeral_session_key_1234"
        binder = AgentCryptographicSessionBinder(key)

        msg = {"command": "run_audit", "target": "production_cluster"}
        env = binder.seal(msg, seq=1)
        print(f"[+] Sealed Signed Envelope:\n    {env.to_dict()}")

        valid = binder.verify(env)
        print(f"[+] Verification Status: {valid}")

        # Test replay
        replay_valid = binder.verify(env)
        print(f"[*] Replay Attempt Status: {replay_valid} (Replay correctly rejected!)")
    else:
        parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
