# MCP outbound network policy

User-configured MCP servers support HTTP(S) with `sse` or `streamable_http`.
By default, every resolved address must be publicly routable. Loopback, private,
link-local (including cloud metadata), reserved, multicast and IPv6 transition
addresses are rejected. Configuration validation checks URL syntax and literal
addresses without resolving user hostnames in the web process. Connection tests,
tool discovery and execution (including previously saved tools) resolve and
connect inside a separate process running as the `sandbox` user.

The web process communicates with this worker using MCP over stdio. The worker
forwards the protocol to the configured SSE or Streamable HTTP endpoint, including
tool schemas, pagination, structured results, errors, progress and cancellation
messages. Credentials and connection configuration travel in the local initialize
message, and are removed before forwarding that message to the remote service.
They are never placed in worker arguments or environment variables.

For a trusted private MCP service, the deployment administrator can set an
explicit comma-separated CIDR allowlist. Prefer individual service addresses:

```yaml
# config.yml
MCP_ALLOWED_NETWORKS: "10.20.30.40/32,fd12:3456::40/128"
```

With environment-based configuration (`MAXKB_CONFIG_TYPE=ENV`), use:

```text
MAXKB_MCP_ALLOWED_NETWORKS=10.20.30.40/32,fd12:3456::40/128
```

Restart the affected services after changing deployment configuration. The list
is deployment-wide, not user-controlled, and permits all ports at those addresses.
Only add trusted MCP service addresses; do not allow entire internal networks or
metadata endpoints. Public addresses remain permitted. A hostname resolving to
multiple addresses is accepted only when every address passes the policy.
An address must also pass `SANDBOX_PYTHON_BANNED_HOSTS`: the MCP allowlist cannot
override the sandbox blacklist. The default image blocks all native IPv6 addresses
with `::/0`, including public IPv6, until the deployment administrator changes that
policy.

Connections resolve and validate DNS again immediately before connecting to a
numeric IP, preserving the original HTTP Host, TLS SNI and certificate verification.
HTTP redirects are disabled; configure the final MCP URL directly. SSE message
endpoints must use the configured origin. Environment HTTP proxies are not used
for MCP connections, so a proxy cannot bypass destination checks. The existing
`sandbox.so` connect hooks provide an additional check of the actual destination.

## Public MCP services behind a Fake-IP DNS proxy

Surge and similar proxies can resolve a public MCP hostname to `198.18.0.0/15`.
These benchmark/Fake-IP addresses are not public destinations and remain blocked.
Configure the proxy to return real DNS addresses for the MCP hostname; do not
allowlist the entire Fake-IP range or hardcode a CDN address in the MCP URL.

For example, append `mcp.amap.com` to `always-real-ip` in the active Surge profile's
`[General]` section, keeping existing entries. Reload the profile and flush DNS,
then verify resolution from inside the MaxKB container. The MCP URL, credentials,
transport and Docker published port (for example `9090:8080`) remain unchanged.
See [Surge's DNS documentation](https://manual.nssurge.com/dns/advanced.html).

Worker stderr distinguishes Fake-IP, network-policy, DNS, certificate, timeout
and HTTP status failures without logging URL parameters or authorization headers.
Unexpected failures continue to use a generic message.

## Deployment requirements

External MCP requires Linux, `SANDBOX=1`, a `sandbox` account, and a running service
able to launch workers and drop their user/group privileges. The existing
`sandbox.c` and `sandbox.so` are reused without changes or new exported symbols.
Deploy the Python changes and restart the affected services; this change does not
require recompiling the sandbox library.

Before accepting MCP configuration, the worker verifies that the process-global
`connect` and `getaddrinfo` symbols come from the configured preloaded library.
After dropping privileges it reads the adjacent `.sandbox.conf` and checks that
at least one blacklist rule actually denies access. IP checks use an invalid file
descriptor; hostname checks require numeric-only resolution. Neither check sends
network traffic. Include at least one literal IP/CIDR or hostname in the blacklist
so the worker can verify a rule (the default image policy already does).

Missing/unrelated libraries, ineffective hooks, unreadable/empty or truncated
network policies, unsupported platforms and disabled sandbox mode fail closed;
there is no fallback to web-process HTTP. Normal denied network requests continue
to be logged; only synthetic startup-probe denial messages are suppressed.

Workers reuse `SANDBOX_PYTHON_PROCESS_LIMIT_MEM_MB` (default 256),
`SANDBOX_PYTHON_PROCESS_LIMIT_CPU_CORES` (default 1), and
`SANDBOX_PYTHON_PROCESS_LIMIT_TIMEOUT_SECONDS` (default 3600). Each session has its
own worker, resource limits and wall deadline. The SDK closes or terminates the
worker on session completion/cancellation. New tool invocations also use workers;
discovering tools does not leave HTTP callbacks in the web process.

MaxKB-generated nested application connections and sandboxed Python tools keep
their existing behavior. Their privilege comes from an in-memory configuration
type created by the server, never from a field in user JSON. Runtime configurations
must not be JSON-serialized between generation and client creation.

Validation completed in a disposable Linux container covered 36 regression tests,
including the existing image's unmodified sandbox library, actual worker UIDs,
resource limits, both transports, subsequent tool calls, pagination, progress,
structured/image results, missing policies, network denial and process cleanup.
Temporary test files were removed after verification.
