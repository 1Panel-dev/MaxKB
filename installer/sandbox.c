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

static const char *BANNED_FILE_NAME = ".SANDBOX_BANNED_HOSTS";

/**
 * 从 .so 文件所在目录读取 .SANDBOX_BANNED_HOSTS 文件内容
 * 返回 malloc 出的字符串（需 free），读取失败则返回空字符串
 */
static char *load_banned_hosts() {
    Dl_info info;
    if (dladdr((void *)load_banned_hosts, &info) == 0 || !info.dli_fname) {
        fprintf(stderr, "[sandbox] ⚠️ Unable to locate shared object path — allowing all hosts\n");
        return strdup("");
    }

    char so_path[PATH_MAX];
    strncpy(so_path, info.dli_fname, sizeof(so_path));
    so_path[sizeof(so_path) - 1] = '\0';

    char *dir = dirname(so_path);
    char file_path[PATH_MAX];
    snprintf(file_path, sizeof(file_path), "%s/%s", dir, BANNED_FILE_NAME);

    FILE *fp = fopen(file_path, "r");
    if (!fp) {
        fprintf(stderr, "[sandbox] ⚠️ Cannot open %s — allowing all hosts\n", file_path);
        return strdup("");
    }

    char *buf = malloc(4096);
    if (!buf) {
        fclose(fp);
        fprintf(stderr, "[sandbox] ⚠️ Memory allocation failed — allowing all hosts\n");
        return strdup("");
    }

    size_t len = fread(buf, 1, 4095, fp);
    buf[len] = '\0';
    fclose(fp);
    return buf;
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
        // 去掉前后空格
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
            } else {
                fprintf(stderr, "[sandbox] ⚠️ Invalid regex '%s' — allowing host by default\n", token);
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

    static char *banned_env = NULL;
    if (!banned_env) banned_env = load_banned_hosts();

    char ip[INET6_ADDRSTRLEN] = {0};
    if (addr->sa_family == AF_INET)
        inet_ntop(AF_INET, &((struct sockaddr_in *)addr)->sin_addr, ip, sizeof(ip));
    else if (addr->sa_family == AF_INET6)
        inet_ntop(AF_INET6, &((struct sockaddr_in6 *)addr)->sin6_addr, ip, sizeof(ip));

    if (banned_env && *banned_env && match_env_patterns(ip, banned_env)) {
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

    static char *banned_env = NULL;
    if (!banned_env) banned_env = load_banned_hosts();

    if (banned_env && *banned_env && node) {
        // 检测 node 是否是 IP
        struct in_addr ipv4;
        struct in6_addr ipv6;
        int is_ip = (inet_pton(AF_INET, node, &ipv4) == 1) ||
                    (inet_pton(AF_INET6, node, &ipv6) == 1);

        // 只对“非IP的域名”进行屏蔽
        if (!is_ip && match_env_patterns(node, banned_env)) {
            fprintf(stderr, "[sandbox] 🚫 Access to host %s is banned (DNS blocked)\n", node);
            return EAI_FAIL; // 模拟 DNS 层禁止
        }
    }

    return real_getaddrinfo(node, service, hints, res);
}
