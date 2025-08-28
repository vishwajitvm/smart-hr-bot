import os
import secrets
import base64

def generate_and_save_key():
    # Generate a random 32-byte key (good for encryption/signing tokens)
    raw_key = secrets.token_bytes(32)
    key = base64.urlsafe_b64encode(raw_key).decode()

    print(f"✅ Generated Encryption Key:\n{key}\n")

    # Save or update in .env file
    env_file = ".env"

    if os.path.exists(env_file):
        lines = []
        updated = False
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("ENCRYPTION_KEY="):
                    lines.append(f"ENCRYPTION_KEY={key}\n")
                    updated = True
                else:
                    lines.append(line)

        if not updated:
            lines.append(f"ENCRYPTION_KEY={key}\n")

        with open(env_file, "w") as f:
            f.writelines(lines)
        print("🔐 Updated ENCRYPTION_KEY in .env file")

    else:
        with open(env_file, "w") as f:
            f.write(f"ENCRYPTION_KEY={key}\n")
        print("📄 Created .env file with ENCRYPTION_KEY")


if __name__ == "__main__":
    generate_and_save_key()
