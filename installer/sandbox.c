#define _GNU_SOURCE
#include <dlfcn.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <regex.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <sys/un.h>
#include <errno.h>
#include <limits.h>
#include <libgen.h>
#include <pwd.h>
#include <stdarg.h>
#include <spawn.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <linux/sched.h>
#include <pty.h>
#include <stdint.h>
#include <stdbool.h>

#define CONFIG_FILE ".sandbox.conf"
#define KEY_BANNED_HOSTS "SANDBOX_PYTHON_BANNED_HOSTS"
#define KEY_ALLOW_DL_PATHS "SANDBOX_PYTHON_ALLOW_DL_PATHS"
#define KEY_ALLOW_SUBPROCESS "SANDBOX_PYTHON_ALLOW_SUBPROCESS"
#define KEY_ALLOW_SYSCALL "SANDBOX_PYTHON_ALLOW_SYSCALL"

static char *banned_hosts = NULL;
static char *allow_dl_paths = NULL;
static int allow_subprocess = 0; // 默认禁止
static int allow_syscall = 0;

static void load_sandbox_config() {
    Dl_info info;
    if (dladdr((void *)load_sandbox_config, &info) == 0 || !info.dli_fname) {
        banned_hosts = strdup("");
        allow_dl_paths = strdup("");
        allow_subprocess = 0;
        allow_syscall = 0;
        return;
    }
    char so_path[PATH_MAX];
    strncpy(so_path, info.dli_fname, sizeof(so_path));
    so_path[sizeof(so_path) - 1] = '\0';
    char *dir = dirname(so_path);
    char config_path[PATH_MAX];
    snprintf(config_path, sizeof(config_path), "%s/%s", dir, CONFIG_FILE);
    FILE *fp = fopen(config_path, "r");
    if (!fp) {
        banned_hosts = strdup("");
        allow_dl_paths = strdup("");
        allow_subprocess = 0;
        allow_syscall = 0;
        return;
    }
    char line[512];
    if (banned_hosts) { free(banned_hosts); banned_hosts = NULL; }
    if (allow_dl_paths) { free(allow_dl_paths); allow_dl_paths = NULL; }
    banned_hosts = strdup("");
    allow_dl_paths = strdup("");
    allow_subprocess = 0;
    allow_syscall = 0;
    while (fgets(line, sizeof(line), fp)) {
        char *key = strtok(line, "=");
        char *value = strtok(NULL, "\n");
        if (!key || !value) continue;
        while (*key == ' ' || *key == '\t') key++;
        char *keyend = key + strlen(key) - 1;
        while (keyend > key && (*keyend == ' ' || *keyend == '\t')) *keyend-- = '\0';
        while (*value == ' ' || *value == '\t') value++;
        char *vend = value + strlen(value) - 1;
        while (vend > value && (*vend == ' ' || *vend == '\t')) *vend-- = '\0';
        if (strcmp(key, KEY_BANNED_HOSTS) == 0) {
            free(banned_hosts);
            banned_hosts = strdup(value);
        } else if (strcmp(key, KEY_ALLOW_DL_PATHS) == 0) {
            free(allow_dl_paths);
            allow_dl_paths = strdup(value);  // 逗号分隔字符串
        } else if (strcmp(key, KEY_ALLOW_SUBPROCESS) == 0) {
            allow_subprocess = atoi(value);
        } else if (strcmp(key, KEY_ALLOW_SYSCALL) == 0) {
            allow_syscall = atoi(value);
        }
    }
    fclose(fp);
}
static void ensure_config_loaded() {
    if (!banned_hosts) load_sandbox_config();
}
static int is_sandbox_user() {
    uid_t uid = getuid();
    struct passwd *pw = getpwuid(uid);
    if (!pw || !pw->pw_name) {
        return 1;  // 无法识别用户 → 认为是 sandbox
    }
    if (strcmp(pw->pw_name, "sandbox") == 0) {
        return 1;
    }
    return 0;
}
static int throw_permission_denied_err(bool whether_to_exit,const char *fmt, ...) {
    va_list ap;
    fputs("Permission denied to ", stderr);
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputs(".\n", stderr);
    errno = EACCES;
    if (whether_to_exit) _exit(126);
    return -1;
}
#define RESOLVE_REAL(func)                      \
    static typeof(func) *real_##func = NULL;    \
    if (!real_##func) {                         \
        real_##func = dlsym(RTLD_NEXT, #func);  \
    }
/**
 * 限制网络访问
 */
// ------------------ 匹配 域名 黑名单 ------------------
static int match_banned_domain(const char *target, const char *rules) {
    if (!target || !rules || !*rules) return 0;
    char *list = strdup(rules);
    char *token = strtok(list, ",");
    int matched = 0;
    while (token) {
        while (*token == ' ' || *token == '\t') token++;
        if (*token) {
            regex_t re;
            char buf[512];
            snprintf(buf, sizeof(buf), "^%s$", token);
            if (regcomp(&re, buf, REG_EXTENDED | REG_NOSUB | REG_ICASE) == 0) {
                if (regexec(&re, target, 0, NULL, 0) == 0)
                    matched = 1;
                regfree(&re);
            }
        }
        if (matched) break;
        token = strtok(NULL, ",");
    }
    free(list);
    return matched;
}
// ------------------ 匹配 IP/CIDR 黑名单 ------------------
static int match_banned_ip(const char *ip_str, const char *rules) {
    if (!ip_str || !rules || !*rules) return 0;
    struct in_addr  ip4;
    struct in6_addr ip6;
    int is_v4 = inet_pton(AF_INET, ip_str, &ip4) == 1;
    int is_v6 = inet_pton(AF_INET6, ip_str, &ip6) == 1;
    if (!is_v4 && !is_v6) return 0;
    char *list = strdup(rules);
    char *token = strtok(list, ",");
    int blocked = 0;
    while (token) {
        while (*token == ' ' || *token == '\t') token++;
        if (!*token) goto next;
        char *slash = strchr(token, '/');
        int prefix = -1;
        if (slash) {
            *slash++ = '\0';
            prefix = atoi(slash);
        }
        /* ---------- IPv4 ---------- */
        if (is_v4) {
            struct in_addr net4;
            if (inet_pton(AF_INET, token, &net4) == 1) {
                if (prefix < 0) {
                    /* 单 IP */
                    if (ip4.s_addr == net4.s_addr) {
                        blocked = 1;
                        break;
                    }
                } else if (prefix >= 0 && prefix <= 32) {
                    uint32_t mask = prefix == 0
                        ? 0
                        : htonl(0xFFFFFFFFu << (32 - prefix));
                    if ((ip4.s_addr & mask) == (net4.s_addr & mask)) {
                        blocked = 1;
                        break;
                    }
                }
            }
        }
        /* ---------- IPv6 ---------- */
        if (is_v6) {
            struct in6_addr net6;
            if (inet_pton(AF_INET6, token, &net6) == 1) {
                if (prefix < 0) {
                    /* 单 IP */
                    if (memcmp(&ip6, &net6, sizeof(ip6)) == 0) {
                        blocked = 1;
                        break;
                    }
                } else if (prefix >= 0 && prefix <= 128) {
                    int full = prefix / 8;
                    int rem  = prefix % 8;
                    if (full &&
                        memcmp(ip6.s6_addr, net6.s6_addr, full) != 0)
                        goto next;
                    if (rem) {
                        uint8_t mask = (uint8_t)(0xFF << (8 - rem));
                        if ((ip6.s6_addr[full] & mask) !=
                            (net6.s6_addr[full] & mask))
                            goto next;
                    }
                    blocked = 1;
                    break;
                }
            }
        }
    next:
        token = strtok(NULL, ",");
    }
    free(list);
    return blocked;
}

// ------------------ 网络拦截 ------------------
int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen) {
    RESOLVE_REAL(connect);
    ensure_config_loaded();
    if (is_sandbox_user() && addr->sa_family == AF_UNIX) {
        struct sockaddr_un *un = (struct sockaddr_un *)addr;
        throw_permission_denied_err(false, "access unix socket: %s", un->sun_path[0] ? un->sun_path : "(abstract)");
        return -1;
    }
    char ip[INET6_ADDRSTRLEN] = {0};
    if (addr->sa_family == AF_INET) {
        inet_ntop(AF_INET,
                  &((struct sockaddr_in *)addr)->sin_addr,
                  ip, sizeof(ip));
    } else if (addr->sa_family == AF_INET6) {
        struct sockaddr_in6 *sin6 = (struct sockaddr_in6 *)addr;
        if (IN6_IS_ADDR_V4MAPPED(&sin6->sin6_addr)) {
            struct in_addr v4;
            memcpy(&v4, &sin6->sin6_addr.s6_addr[12], sizeof(v4));
            inet_ntop(AF_INET, &v4, ip, sizeof(ip));
        } else {
            inet_ntop(AF_INET6, &sin6->sin6_addr, ip, sizeof(ip));
        }
    }
    if (is_sandbox_user() && match_banned_ip(ip, banned_hosts)) {
        throw_permission_denied_err(false, "access %s", ip);
        return -1;
    }
    return real_connect(sockfd, addr, addrlen);
}
int getaddrinfo(const char *node, const char *service,
                const struct addrinfo *hints,
                struct addrinfo **res) {
    RESOLVE_REAL(getaddrinfo);
    ensure_config_loaded();
    if (node && is_sandbox_user()) {
        struct in_addr ip4;
        struct in6_addr ip6;
        int is_ip = inet_pton(AF_INET, node, &ip4) == 1 ||
                    inet_pton(AF_INET6, node, &ip6) == 1;
        if (!is_ip && match_banned_domain(node, banned_hosts)) {
            throw_permission_denied_err(false, "access %s", node);
            return EAI_SYSTEM;
        }
    }
    return real_getaddrinfo(node, service, hints, res);
}
/**
 * 限制创建子进程
 */
static int allow_create_subprocess() {
    ensure_config_loaded();
    return allow_subprocess || !is_sandbox_user();
}
static int not_supported(const char *function_name) {
    fprintf(stderr, "Not supported function: %s\n", function_name);
    _exit(126);
    return -1;
}
int execv(const char *path, char *const argv[]) {
    RESOLVE_REAL(execv);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_execv(path, argv);
}
int __execv(const char *path, char *const argv[]) {
    return execv(path, argv);
}
int execve(const char *filename, char *const argv[], char *const envp[]) {
    RESOLVE_REAL(execve);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_execve(filename, argv, envp);
}
int __execve(const char *filename, char *const argv[], char *const envp[]) {
    return execve(filename, argv, envp);
}
int execveat(int dirfd, const char *pathname,
             char *const argv[], char *const envp[], int flags) {
    RESOLVE_REAL(execveat);
    if (!allow_create_subprocess())  return throw_permission_denied_err(true, "create subprocess");
    return real_execveat(dirfd, pathname, argv, envp, flags);
}
int execvpe(const char *file, char *const argv[], char *const envp[]) {
    RESOLVE_REAL(execvpe);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_execvpe(file, argv, envp);
}
int __execvpe(const char *file, char *const argv[], char *const envp[]) {
    return execvpe(file, argv, envp);
}
int execvp(const char *file, char *const argv[]) {
    RESOLVE_REAL(execvp);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_execvp(file, argv);
}
int __execvp(const char *file, char *const argv[]) {
    return execvp(file, argv);
}
int execl(const char *path, const char *arg, ...) {
    return not_supported("execl");
}
int __execl(const char *path, const char *arg, ...) {
    return not_supported("__execl");
}
int execlp(const char *file, const char *arg, ...) {
    return not_supported("execlp");
}
int __execlp(const char *file, const char *arg, ...) {
    return not_supported("__execlp");
}
int execle(const char *path, const char *arg, ...) {
    return not_supported("execle");
}
pid_t fork(void) {
    RESOLVE_REAL(fork);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_fork();
}
pid_t __fork(void) {
    return fork();
}
pid_t vfork(void) {
    RESOLVE_REAL(vfork);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_vfork();
}
pid_t __vfork(void) {
    return vfork();
}
int clone(int (*fn)(void *), void *child_stack, int flags, void *arg, ...) {
    RESOLVE_REAL(clone);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    va_list ap;
    va_start(ap, arg);
    long a4 = va_arg(ap, long);
    long a5 = va_arg(ap, long);
    va_end(ap);
    return real_clone(fn, child_stack, flags, arg, (void *)a4, (void *)a5);
}
int clone3(struct clone_args *cl_args, size_t size) {
    RESOLVE_REAL(clone3);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_clone3(cl_args, size);
}
int posix_spawn(pid_t *pid, const char *path,
                const posix_spawn_file_actions_t *file_actions,
                const posix_spawnattr_t *attrp,
                char *const argv[], char *const envp[]) {
    RESOLVE_REAL(posix_spawn);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_posix_spawn(pid, path, file_actions, attrp, argv, envp);
}
int __posix_spawn(pid_t *pid, const char *path,
                  const posix_spawn_file_actions_t *file_actions,
                  const posix_spawnattr_t *attrp,
                  char *const argv[], char *const envp[]) {
    return posix_spawn(pid, path, file_actions, attrp, argv, envp);
}
int posix_spawnp(pid_t *pid, const char *file,
                 const posix_spawn_file_actions_t *file_actions,
                 const posix_spawnattr_t *attrp,
                 char *const argv[], char *const envp[]) {
    RESOLVE_REAL(posix_spawnp);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_posix_spawnp(pid, file, file_actions, attrp, argv, envp);
}
int __posix_spawnp(pid_t *pid, const char *file,
                   const posix_spawn_file_actions_t *file_actions,
                   const posix_spawnattr_t *attrp,
                   char *const argv[], char *const envp[]) {
    return posix_spawnp(pid, file, file_actions, attrp, argv, envp);
}
FILE *popen(const char *command, const char *type) {
    RESOLVE_REAL(popen);
    if (!allow_create_subprocess()) {
        fprintf(stderr, "Permission denied to create subprocess.\n");
        errno = EACCES;
        return NULL;
    }
    return real_popen(command, type);
}
FILE *__popen(const char *command, const char *type) {
    return popen(command, type);
}
int system(const char *command) {
    RESOLVE_REAL(system);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_system(command);
}
int __libc_system(const char *command) {
    RESOLVE_REAL(__libc_system);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real___libc_system(command);
}
pid_t __libc_clone(int (*fn)(void *), void *child_stack, int flags, void *arg, ...) {
    RESOLVE_REAL(__libc_clone);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    va_list ap;
    va_start(ap, arg);
    long a4 = va_arg(ap, long);
    long a5 = va_arg(ap, long);
    va_end(ap);
    return real___libc_clone(fn, child_stack, flags, arg, (void *)a4, (void *)a5);
}

pid_t forkpty(int *amaster, char *name, const struct termios *termp, const struct winsize *winp) {
    RESOLVE_REAL(forkpty);
    if (!allow_create_subprocess()) return throw_permission_denied_err(true, "create subprocess");
    return real_forkpty(amaster, name, termp, winp);
}
pid_t __forkpty(int *amaster, char *name, const struct termios *termp, const struct winsize *winp) {
    return forkpty(amaster, name, termp, winp);
}
/**
 * 限制调用syscall
 */
static int allow_access_syscall() {
    ensure_config_loaded();
    return allow_syscall || !is_sandbox_user();
}
long (*real_syscall)(long, ...) = NULL;
long syscall(long number, ...) {
    RESOLVE_REAL(syscall);
    va_list ap;
    va_start(ap, number);
    long a1 = va_arg(ap, long);
    long a2 = va_arg(ap, long);
    long a3 = va_arg(ap, long);
    long a4 = va_arg(ap, long);
    long a5 = va_arg(ap, long);
    long a6 = va_arg(ap, long);
    va_end(ap);
    switch (number) {
        case SYS_execve:
        case SYS_execveat:
#ifdef SYS_fork
        case SYS_fork:
#endif
#ifdef SYS_vfork
        case SYS_vfork:
#endif
        case SYS_clone:
        case SYS_clone3:
#ifdef SYS_posix_spawn
        case SYS_posix_spawn:
#endif
#ifdef SYS_posix_spawnp
        case SYS_posix_spawnp:
#endif
        case SYS_socket:
        case SYS_connect:
        case SYS_bind:
        case SYS_listen:
        case SYS_accept:
        case SYS_accept4:
        case SYS_sendto:
        case SYS_recvmsg:
        case SYS_getsockopt:
        case SYS_setsockopt:
        case SYS_ptrace:
        case SYS_setuid:
        case SYS_setgid:
        case SYS_reboot:
        case SYS_mount:
#ifdef SYS_chown
        case SYS_chown:
#endif
#ifdef SYS_chmod
        case SYS_chmod:
#endif
        case SYS_fchmodat:
        case SYS_mprotect:
#ifdef SYS_open
        case SYS_open:
#endif
        case SYS_openat:
        case SYS_swapon:
        case SYS_swapoff:
        case SYS_kill:
        case SYS_mmap:
        case SYS_munmap:
        case SYS_memfd_create:
        case SYS_shmat:
        case SYS_shmget:
        case SYS_shmctl:
        case SYS_prctl:
            if (!allow_access_syscall()) {
                throw_permission_denied_err(true, "access syscall %ld", number);
             }
    }
    return real_syscall(number, a1, a2, a3, a4, a5, a6);
}

/**
 * 限制加载动态链接库
 */
static int is_in_allow_dl_paths(const char *filename) {
    if (!filename || !*filename) return 1;
    ensure_config_loaded();
    if (!allow_dl_paths || !*allow_dl_paths) return 0;
    char real_file[PATH_MAX];
    if (!realpath(filename, real_file)) return 0;
    char *rules = strdup(allow_dl_paths);
    if (!rules) return 0;
    int allowed = 0;
    char *saveptr = NULL;
    for (char *token = strtok_r(rules, ",", &saveptr); token; token = strtok_r(NULL, ",", &saveptr)) {
        while (*token == ' ' || *token == '\t') token++;
        if (!*token) continue;
        char real_rule[PATH_MAX];
        if (!realpath(token, real_rule)) continue;
        size_t len = strlen(real_rule);
        if (strncmp(real_file, real_rule, len) == 0 &&
            (real_file[len] == '\0' || real_file[len] == '/')) {
            allowed = 1;
            break;
        }
    }
    free(rules);
    return allowed;
}
void *dlopen(const char *filename, int flag) {
    RESOLVE_REAL(dlopen);
    if (is_sandbox_user() && !is_in_allow_dl_paths(filename)) {
        throw_permission_denied_err(true, "access file %s", filename);
    }
    return real_dlopen(filename, flag);
}
void *__dlopen(const char *filename, int flag) {
    return dlopen(filename, flag);
}
void *dlmopen(Lmid_t lmid, const char *filename, int flags) {
    RESOLVE_REAL(dlmopen);
    if (is_sandbox_user() && !is_in_allow_dl_paths(filename)) {
        throw_permission_denied_err(true, "access file %s", filename);
    }
    return real_dlmopen(lmid, filename, flags);
}
void *__dlmopen(Lmid_t lmid, const char *filename, int flags) {
    return dlmopen(lmid, filename, flags);
}
void* mmap(void *addr, size_t len, int prot, int flags, int fd, off_t off) {
    RESOLVE_REAL(mmap);
    if (is_sandbox_user() && (prot & PROT_EXEC)) {
        if ((flags & MAP_ANONYMOUS) || fd < 0) { //匿名映射：直接拒绝
            throw_permission_denied_err(true, "mmap(anonymous)");
        }
        char link[64];
        snprintf(link, sizeof(link), "/proc/self/fd/%d", fd);
        char real_path[PATH_MAX];
        ssize_t n = readlink(link, real_path, sizeof(real_path) - 1);
        if (n < 0) {
            throw_permission_denied_err(true, "mmap(readlink failed)");
        }
        real_path[n] = '\0';
        if (!is_in_allow_dl_paths(real_path)) {
            throw_permission_denied_err(true, "mmap %s", real_path);
        }
    }
    return real_mmap(addr, len, prot, flags, fd, off);
}
void* mmap64(void *addr, size_t len, int prot, int flags, int fd, off_t off) {
    return mmap(addr, len, prot, flags, fd, off);
}
int mprotect(void *addr, size_t len, int prot) {
    RESOLVE_REAL(mprotect);
    if (is_sandbox_user() && (prot & PROT_EXEC)) {
        throw_permission_denied_err(true, "mprotect");
    }
    return real_mprotect(addr, len, prot);
}