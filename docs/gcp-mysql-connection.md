Picture your local machine and your Cloud SQL instance as two mildly shy creatures who want to talk but won’t unless you set up the right handshake. Google, being Google, wraps everything in a few layers of networking labyrinths, but once you know the paths, it’s smooth.

Let’s keep things practical and clean.

First thing: you **never** expose a Cloud SQL instance directly to the public internet unless you absolutely have to. The two sane patterns are:

1. Use the **Cloud SQL Auth Proxy** (the safest, easiest).
2. Use **Private IP** + a VPN/Cloud Router + VPC Peering (if you want full network integration).

Since you want “local application → Cloud SQL MySQL,” the Auth Proxy is your friend. It’s basically a little program that sits on your machine and securely tunnels traffic to the database.

---

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

### If you want the “network engineer with caffeine” path

If you prefer Private IP networking:

• Enable **Private IP** on the Cloud SQL instance.
• Create a **VPC network** that the instance belongs to.
• From your local machine, build a connection like:
– Cloud VPN (site-to-site)
– Or Cloud Router + HA VPN
– Or open a secure SSH tunnel through a GCE VM inside the VPC.

This gives you a stable internal IP (10.x.x.x), but setup is heavier.

---

### Quick sanity checks

If connection fails:

• Make sure the MySQL user has the right host permissions (`%` or proxy-specific).
• Ensure MySQL password is correct.
• Confirm your IAM user can connect (`Cloud SQL Client`).
• Check whether your instance uses public or private IP; for proxy it doesn’t matter, but direct connections do.

---

If you tell me your instance details (public/private IP, whether you prefer proxy or private networking, and what language/framework your app uses), I can give you exact commands and connection snippets tailored to your setup.


Your proxy is basically saying: *“Friend, you never logged me into Google.”*
Cloud SQL Proxy needs **Application Default Credentials (ADC)** — which on your local machine means you must authenticate using `gcloud auth login` (and sometimes `gcloud auth application-default login` depending on setup).

Let’s get you unstuck cleanly.

---

## Why this error happens

You did log into gcloud earlier, but the proxy looks for **Application Default Credentials**, not just standard gcloud credentials. They are stored separately.

Hence:

```
credentials: could not find default credentials
```

Time to give the proxy something to chew on.

---

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

## If it still fails…

I can walk you through:

• direct connection using public IP
• service account JSON file auth
• or Private IP + VPN

But 99% of local dev setups work after running the ADC login command.

Whenever you're ready, I can help you craft the exact connection string for your app (Python, Node, Java, etc.).

```powershell
pip install mysql-connector-python
```