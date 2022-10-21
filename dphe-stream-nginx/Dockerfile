# Parent image
FROM redhat/ubi8:8.6

LABEL description="DeepPhe Stream Docker Nginx Image"

# When trying to run "yum updates" or "yum install" the "system is not registered with an entitlement server" error message is given
# To fix this issue:
RUN echo $'[main]\n\
enabled=0\n\\n\
# When following option is set to 1, then all repositories defined outside redhat.repo will be disabled\n\
# every time subscription-manager plugin is triggered by dnf or yum\n\
disable_system_repos=0\n'\
>> /etc/yum/pluginconf.d/subscription-manager.conf

# Change to directory that contains the Dockerfile
WORKDIR /usr/src/app

# Copy from host to image
COPY . .

# http://nginx.org/en/linux_packages.html#RHEL-CentOS
# Set up the yum repository to install the latest mainline version of Nginx
RUN echo $'[nginx-mainline]\n\
name=nginx mainline repo\n\
baseurl=http://nginx.org/packages/mainline/centos/$releasever/$basearch/\n\
gpgcheck=1\n\
enabled=0\n\
gpgkey=https://nginx.org/keys/nginx_signing.key\n\
module_hotfixes=true\n'\
>> /etc/yum.repos.d/nginx.repo

# Reduce the number of layers in image by minimizing the number of separate RUN commands
# Update packages
# Install the prerequisites
# By default, the repository for stable nginx packages is used. We would like to use mainline nginx packages
# Remove the default nginx config file
# Overwrite the nginx.conf with ours to run nginx as non-root
# Install Python 3.9
# Set default Python version for `python` command, `python3` already points to the newly installed Python3.9
# Upgrade pip, after upgrading, both pip and pip3 are the same version
# Install the Python dependencies of integration test
# Clean all yum cache
# Copy the entrypoint script and make it executible
# Install gosu for de-elevating root to deepphe user
RUN yum update -y && \
    yum install -y yum-utils && \
    yum-config-manager --enable nginx-mainline && \
    yum install -y nginx && \
    rm /etc/nginx/conf.d/default.conf && \
    mv nginx.conf /etc/nginx/nginx.conf && \
    rm -rf nginx && \
    yum install -y python39 && \
    alternatives --set python /usr/bin/python3.9 && \
    pip3 install --upgrade pip && \
    pip3 install -r integration-test/requirements.txt && \
    yum clean all && \
    cp /usr/src/app/entrypoint.sh /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh && \
    curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.14/gosu-amd64" && \
    curl -o /usr/local/bin/gosu.asc -SL "https://github.com/tianon/gosu/releases/download/1.14/gosu-amd64.asc" && \
    rm /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu

# Set an entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. 
# Here 8080 for nginx running as non-root
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]