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
#include <errno.h>
#include <limits.h>
#include <libgen.h>
#include <pwd.h>
#include <stdarg.h>
#include <spawn.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <time.h>
#include <execinfo.h>
#include <dlfcn.h>
#include <linux/sched.h>
#include <pty.h>

#define CONFIG_FILE ".sandbox.conf"
#define KEY_BANNED_HOSTS "SANDBOX_PYTHON_BANNED_HOSTS"
#define KEY_ALLOW_SUBPROCESS "SANDBOX_PYTHON_ALLOW_SUBPROCESS"

static char *banned_hosts = NULL;
static int allow_subprocess = 0; // 默认禁止

static void load_sandbox_config() {
     Dl_info info;
     if (dladdr((void *)load_sandbox_config, &info) == 0 || !info.dli_fname) {
         banned_hosts = strdup("");
         allow_subprocess = 0;
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
         allow_subprocess = 0;
         return;
     }
    char line[512];
    banned_hosts = strdup("");
    allow_subprocess = 0;
    while (fgets(line, sizeof(line), fp)) {
        char *key = strtok(line, "=");
        char *value = strtok(NULL, "\n");
        if (!key || !value) continue;
        while (*key == ' ' || *key == '\t') key++;
        char *kend = key + strlen(key) - 1;
        while (kend > key && (*kend == ' ' || *kend == '\t')) *kend-- = '\0';
        while (*value == ' ' || *value == '\t') value++;
        char *vend = value + strlen(value) - 1;
        while (vend > value && (*vend == ' ' || *vend == '\t')) *vend-- = '\0';
        if (strcmp(key, KEY_BANNED_HOSTS) == 0) {
            free(banned_hosts);
            banned_hosts = strdup(value);
        } else if (strcmp(key, KEY_ALLOW_SUBPROCESS) == 0) {
            allow_subprocess = atoi(value);
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
        return 1;  // 无法识别用户 → 认为是sandbox
    }
    if (strcmp(pw->pw_name, "sandbox") == 0) {
        return 1;
    }
    return 0;
}
/**
 * 精确匹配黑名单
 */
static int match_env_patterns(const char *target, const char *env_val) {
    if (!target || !env_val || !*env_val) return 0;
    char *patterns = strdup(env_val);
    char *token = strtok(patterns, ",");
    int matched = 0;
    while (token) {
        while (*token == ' ' || *token == '\t') token++;
        char *end = token + strlen(token) - 1;
        while (end > token && (*end == ' ' || *end == '\t')) *end-- = '\0';
        if (*token) {
            regex_t regex;
            char fullpattern[512];
            snprintf(fullpattern, sizeof(fullpattern), "^%s$", token);
            if (regcomp(&regex, fullpattern, REG_EXTENDED | REG_NOSUB | REG_ICASE) == 0) {
                if (regexec(&regex, target, 0, NULL, 0) == 0) {
                    matched = 1;
                    regfree(&regex);
                    break;
                }
                regfree(&regex);
            }
        }
        token = strtok(NULL, ",");
    }
    free(patterns);
    return matched;
}

/** 拦截 connect() —— 精确匹配 IP */
int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen) {
    static int (*real_connect)(int, const struct sockaddr *, socklen_t) = NULL;
    if (!real_connect)
        real_connect = dlsym(RTLD_NEXT, "connect");
    ensure_config_loaded();
    char ip[INET6_ADDRSTRLEN] = {0};
    if (addr->sa_family == AF_INET)
        inet_ntop(AF_INET, &((struct sockaddr_in *)addr)->sin_addr, ip, sizeof(ip));
    else if (addr->sa_family == AF_INET6)
        inet_ntop(AF_INET6, &((struct sockaddr_in6 *)addr)->sin6_addr, ip, sizeof(ip));
    if (is_sandbox_user() && banned_hosts && *banned_hosts && match_env_patterns(ip, banned_hosts)) {
        fprintf(stderr, "[sandbox] 🚫 Access to host %s is banned\n", ip);
        errno = EACCES; // EACCES 的值是 13, 意思是 Permission denied
        return -1;
    }
    return real_connect(sockfd, addr, addrlen);
}

/** 拦截 getaddrinfo() —— 只拦截域名，不拦截纯 IP */
int getaddrinfo(const char *node, const char *service,
                const struct addrinfo *hints, struct addrinfo **res) {
    static int (*real_getaddrinfo)(const char *, const char *,
                                   const struct addrinfo *, struct addrinfo **) = NULL;
    if (!real_getaddrinfo)
        real_getaddrinfo = dlsym(RTLD_NEXT, "getaddrinfo");
    ensure_config_loaded();
    if (banned_hosts && *banned_hosts && node) {
        // 检测 node 是否是 IP
        struct in_addr ipv4;
        struct in6_addr ipv6;
        int is_ip = (inet_pton(AF_INET, node, &ipv4) == 1) ||
                    (inet_pton(AF_INET6, node, &ipv6) == 1);
        // 只对“非IP的域名”进行屏蔽
        if (is_sandbox_user() && !is_ip && match_env_patterns(node, banned_hosts )) {
            fprintf(stderr, "[sandbox] 🚫 Access to host %s is banned (DNS blocked)\n", node);
            return EAI_FAIL; // 模拟 DNS 层禁止
        }
    }
    return real_getaddrinfo(node, service, hints, res);
}
/* ------------------ 禁止创建子进程------------------ */
static int allow_create_subprocess() {
    ensure_config_loaded();
    return allow_subprocess || !is_sandbox_user();
}
static int deny() {
    fprintf(stderr, "Permission denied to create subprocess.\n");
    _exit(1);
    return -1;
}
static int not_supported(const char *function_name) {
    fprintf(stderr, "Not supported function: %s\n", function_name);
    _exit(1);
    return -1;
}
#define RESOLVE_REAL(func)                      \
    static typeof(func) *real_##func = NULL;    \
    if (!real_##func) {                         \
        real_##func = dlsym(RTLD_NEXT, #func);  \
    }
int execv(const char *path, char *const argv[]) {
    RESOLVE_REAL(execv);
    if (!allow_create_subprocess() && strstr(path, "bin/python") == NULL)  return deny();
    return real_execv(path, argv);
}
int __execv(const char *path, char *const argv[]) {
    RESOLVE_REAL(__execv);
    if (!allow_create_subprocess() && strstr(path, "bin/python") == NULL)  return deny();
    return real___execv(path, argv);
}
int execve(const char *filename, char *const argv[], char *const envp[]) {
    RESOLVE_REAL(execve);
    if (!allow_create_subprocess()) return deny();
    return real_execve(filename, argv, envp);
}
int __execve(const char *filename, char *const argv[], char *const envp[]) {
    RESOLVE_REAL(__execve);
    if (!allow_create_subprocess()) return deny();
    return real___execve(filename, argv, envp);
}
int execveat(int dirfd, const char *pathname,
             char *const argv[], char *const envp[], int flags) {
    RESOLVE_REAL(execveat);
    if (!allow_create_subprocess())  return deny();
    return real_execveat(dirfd, pathname, argv, envp, flags);
}
int execvpe(const char *file, char *const argv[], char *const envp[]) {
    return not_supported("execvpe");
}
int __execvpe(const char *file, char *const argv[], char *const envp[]) {
    return not_supported("__execvpe");
}
int execvp(const char *file, char *const argv[]) {
    return not_supported("execvp");
}
int __execvp(const char *file, char *const argv[]) {
    return not_supported("__execvp");
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
    if (!allow_create_subprocess()) return deny();
    return real_fork();
}
pid_t __fork(void) {
    RESOLVE_REAL(__fork);
    if (!allow_create_subprocess()) return deny();
    return real___fork();
}
pid_t vfork(void) {
    RESOLVE_REAL(vfork);
    if (!allow_create_subprocess()) return deny();
    return real_vfork();
}
pid_t __vfork(void) {
    RESOLVE_REAL(__vfork);
    if (!allow_create_subprocess()) return deny();
    return real___vfork();
}
int clone(int (*fn)(void *), void *child_stack, int flags, void *arg, ...) {
    RESOLVE_REAL(clone);
    if (!allow_create_subprocess()) return deny();
    va_list ap;
    va_start(ap, arg);
    long a4 = va_arg(ap, long);
    long a5 = va_arg(ap, long);
    va_end(ap);
    return real_clone(fn, child_stack, flags, arg, (void *)a4, (void *)a5);
}
int clone3(struct clone_args *cl_args, size_t size) {
    RESOLVE_REAL(clone3);
    if (!allow_create_subprocess()) return deny();
    return real_clone3(cl_args, size);
}
int posix_spawn(pid_t *pid, const char *path,
                const posix_spawn_file_actions_t *file_actions,
                const posix_spawnattr_t *attrp,
                char *const argv[], char *const envp[]) {
    RESOLVE_REAL(posix_spawn);
    if (!allow_create_subprocess()) return deny();
    return real_posix_spawn(pid, path, file_actions, attrp, argv, envp);
}

int posix_spawnp(pid_t *pid, const char *file,
                 const posix_spawn_file_actions_t *file_actions,
                 const posix_spawnattr_t *attrp,
                 char *const argv[], char *const envp[]) {
    RESOLVE_REAL(posix_spawnp);
    if (!allow_create_subprocess()) return deny();
    return real_posix_spawnp(pid, file, file_actions, attrp, argv, envp);
}
int __posix_spawn(pid_t *pid, const char *path,
                  const posix_spawn_file_actions_t *file_actions,
                  const posix_spawnattr_t *attrp,
                  char *const argv[], char *const envp[]) {
    RESOLVE_REAL(__posix_spawn);
    if (!allow_create_subprocess()) return deny();
    return real___posix_spawn(pid, path, file_actions, attrp, argv, envp);
}

int __posix_spawnp(pid_t *pid, const char *file,
                   const posix_spawn_file_actions_t *file_actions,
                   const posix_spawnattr_t *attrp,
                   char *const argv[], char *const envp[]) {
    RESOLVE_REAL(__posix_spawnp);
    if (!allow_create_subprocess()) return deny();
    return real___posix_spawnp(pid, file, file_actions, attrp, argv, envp);
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
    RESOLVE_REAL(__popen);
    if (!allow_create_subprocess()) {
        fprintf(stderr, "Permission denied to create subprocess.\n");
        errno = EACCES;
        return NULL;
    }
    return real___popen(command, type);
}
int system(const char *command) {
    RESOLVE_REAL(system);
    if (!allow_create_subprocess()) return deny();
    return real_system(command);
}
int __libc_system(const char *command) {
    RESOLVE_REAL(__libc_system);
    if (!allow_create_subprocess()) return deny();
    return real___libc_system(command);
}
pid_t __libc_clone(int (*fn)(void *), void *child_stack, int flags, void *arg, ...) {
    RESOLVE_REAL(__libc_clone);
    if (!allow_create_subprocess()) return deny();
    va_list ap;
    va_start(ap, arg);
    long a4 = va_arg(ap, long);
    long a5 = va_arg(ap, long);
    va_end(ap);
    return real___libc_clone(fn, child_stack, flags, arg, (void *)a4, (void *)a5);
}
pid_t forkpty(int *amaster, char *name, const struct termios *termp, const struct winsize *winp) {
    RESOLVE_REAL(forkpty);
    if (!allow_create_subprocess()) return deny();
    return real_forkpty(amaster, name, termp, winp);
}
pid_t __forkpty(int *amaster, char *name, const struct termios *termp, const struct winsize *winp) {
    RESOLVE_REAL(__forkpty);
    if (!allow_create_subprocess()) return deny();
    return real___forkpty(amaster, name, termp, winp);
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
            if (!allow_create_subprocess()) return deny();
    }
    return real_syscall(number, a1, a2, a3, a4, a5, a6);
}