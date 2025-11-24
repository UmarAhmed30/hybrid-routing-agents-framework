### The smooth path: Cloud SQL Auth Proxy

1. **Install the Cloud SQL Auth Proxy**

   Download from:
   [https://cloud.google.com/sql/docs/mysql/sql-proxy#install](https://cloud.google.com/sql/docs/mysql/sql-proxy#install)

   Example on Linux/macOS:

   ```bash
   curl -o cloud-sql-proxy https://dl.google.com/cloudsql/cloud-sql-proxy.linux.amd64
   chmod +x cloud-sql-proxy
   ```

   Windows:
   Download the `.exe` and put it somewhere in PATH.

2. **Enable IAM auth + get credentials**

   Login with:

   ```bash
   gcloud auth login
   gcloud config set project <your-project>
   ```

   Your user must have:

   * Cloud SQL Client role
   * (Optional but recommended) Cloud SQL Instance Viewer

3. **Find your instance connection name**

   Run:

   ```bash
   gcloud sql instances describe <INSTANCE_NAME> --format="value(connectionName)"
   ```

   It looks like:

   ```
   project:region:instance
   ```

4. **Run the proxy to open a local port**

   Example:

   ```bash
   ./cloud-sql-proxy project:region:instance
   ```

   By default it exposes:

   ```
   localhost:3306
   ```

   If your local machine already uses 3306, pick another port:

   ```bash
   ./cloud-sql-proxy --port=3307 project:region:instance
   ```

5. **Connect from your application exactly like a local MySQL DB**

   For example:

   ```
   host: 127.0.0.1
   port: 3306  (or 3307)
   user: <mysql-username>
   password: <mysql-password>
   db: <database-name>
   ```

   That’s all. Your app thinks the DB is local, but the proxy keeps everything secure.

---

### Quick sanity checks

If connection fails:

• Make sure the MySQL user has the right host permissions (`%` or proxy-specific).
• Ensure MySQL password is correct.
• Confirm your IAM user can connect (`Cloud SQL Client`).
• Check whether your instance uses public or private IP; for proxy it doesn’t matter, but direct connections do.

---

## Why this error happens

## Fix (Works 99% of the time)

### Step 1: Authenticate your local machine with ADC

Run:

```bash
gcloud auth application-default login
```

This opens a browser → pick your Google account → approve.

This creates the file:

```
C:\Users\<you>\AppData\Roaming\gcloud\application_default_credentials.json
```

That’s exactly what Cloud SQL Proxy wants.

---

### Step 2: Verify ADC installed

Run:

```bash
gcloud auth application-default print-access-token
```

If it prints a long token, you’re good.

---

### Step 3: Run the proxy again

```bash
cloud-sql-proxy.x64 high-function-471300-r8:us-central1:sys-ml-model-registry
```

Now it should bind to:

```
localhost:3306
```

If port is busy:

```bash
cloud-sql-proxy.x64 --port=3307 high-function-471300-r8:us-central1:sys-ml-model-registry
```

---

## Step 4: Connect from your MySQL client or app

Host:

```
127.0.0.1
```

Port:

```
3306 (or your custom port)
```

User/password:
Your Cloud SQL MySQL user.

DB name:
Whatever you created.

---

```powershell
pip install mysql-connector-python
```
