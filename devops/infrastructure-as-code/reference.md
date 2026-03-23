# 基础设施即代码参考文档

## 基础设施即代码概述

### 什么是IaC
基础设施即代码（Infrastructure as Code，IaC）是一种通过代码来管理和配置基础设施的方法，它将基础设施视为软件来处理，使用版本控制、自动化和可重复的流程来管理IT资源。

### IaC的核心原则
1. **声明式配置**: 描述期望的状态，而不是如何达到该状态
2. **版本控制**: 所有基础设施配置都在版本控制系统中管理
3. **自动化**: 通过自动化工具来创建、修改和删除基础设施
4. **可重复性**: 能够在不同环境中重复创建相同的基础设施
5. **不可变性**: 通过替换而不是修改来管理基础设施变更

### IaC的优势
- **一致性**: 确保所有环境的基础设施配置一致
- **可追溯性**: 通过版本控制追踪所有变更
- **自动化**: 减少手动操作，降低人为错误
- **可扩展性**: 快速复制和扩展基础设施
- **成本控制**: 优化资源使用，降低成本

## Terraform详解

### Terraform基础概念

#### HCL语法基础
```hcl
# main.tf - 基础配置示例

# 定义AWS提供商
provider "aws" {
  region = "us-west-2"
}

# 定义VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "main-vpc"
    Environment = "production"
    Project     = "web-app"
  }
}

# 定义子网
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-west-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-1"
  }
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "private-subnet-1"
  }
}

# 定义安全组
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg"
  }
}

# 定义EC2实例
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]

  tags = {
    Name = "web-server-1"
  }
}

# 输出值
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "The ID of the public subnet"
  value       = aws_subnet.public.id
}

output "web_server_public_ip" {
  description = "The public IP of the web server"
  value       = aws_instance.web.public_ip
}
```

#### 变量和数据源
```hcl
# variables.tf - 变量定义
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

# data.tf - 数据源定义
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# locals.tf - 本地变量
locals {
  common_tags = {
    Project     = "web-app"
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  az_names = slice(data.aws_availability_zones.available.names, 0, 2)
}
```

#### 模块化设计
```hcl
# modules/vpc/main.tf - VPC模块
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Enable NAT gateway"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.tags, {
    Name = "main-vpc"
  })
}

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(var.tags, {
    Name = "public-subnet-${count.index + 1}"
  })
}

resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(var.tags, {
    Name = "private-subnet-${count.index + 1}"
  })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = merge(var.tags, {
    Name = "main-igw"
  })
}

resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? 1 : 0
  vpc  = true

  tags = merge(var.tags, {
    Name = "nat-eip"
  })

  depends_on = [aws_internet_gateway.this]
}

resource "aws_nat_gateway" "this" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(var.tags, {
    Name = "main-nat-gateway"
  })

  depends_on = [aws_internet_gateway.this]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = merge(var.tags, {
    Name = "public-rt"
  })
}

resource "aws_route_table" "private" {
  count = var.enable_nat_gateway ? 1 : 0
  vpc_id = aws_vpc.this.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this[0].id
  }

  tags = merge(var.tags, {
    Name = "private-rt"
  })
}

resource "aws_route_table_association" "public" {
  count = length(var.public_subnet_cidrs)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = length(var.private_subnet_cidrs)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[0].id
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "internet_gateway_id" {
  description = "The ID of the internet gateway"
  value       = aws_internet_gateway.this.id
}

# 使用VPC模块
# main.tf
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr               = var.vpc_cidr
  public_subnet_cidrs    = var.public_subnet_cidrs
  private_subnet_cidrs   = var.private_subnet_cidrs
  availability_zones     = data.aws_availability_zones.available.names
  enable_nat_gateway     = true
  tags = {
    Environment = var.environment
    Project     = "web-app"
  }
}
```

### Terraform高级特性

#### 工作空间管理
```hcl
# terraform.tfvars.dev - 开发环境配置
environment = "development"
vpc_cidr    = "10.0.0.0/16"
instance_type = "t3.micro"

# terraform.tfvars.prod - 生产环境配置
environment = "production"
vpc_cidr    = "10.1.0.0/16"
instance_type = "t3.medium"

# 使用工作空间
terraform workspace new development
terraform workspace new production
terraform workspace select development
terraform apply -var-file="terraform.tfvars.dev"
```

#### 状态管理
```bash
# 远程状态配置
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "web-app/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

# 状态管理命令
terraform state list
terraform state show aws_vpc.main
terraform state mv aws_instance.web aws_instance.web_new
terraform state rm aws_instance.old
terraform import aws_vpc.main vpc-12345678
```

#### Provider配置
```hcl
# 多provider配置
provider "aws" {
  region = "us-west-2"
  alias  = "west"
}

provider "aws" {
  region = "us-east-1"
  alias  = "east"
}

# 使用别名provider
resource "aws_vpc" "west" {
  provider = aws.west
  cidr_block = "10.0.0.0/16"
}

resource "aws_vpc" "east" {
  provider = aws.east
  cidr_block = "10.1.0.0/16"
}
```

## AWS CloudFormation详解

### CloudFormation基础

#### 模板结构
```yaml
# template.yaml - CloudFormation模板
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Web Application Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: development
    AllowedValues:
      - development
      - staging
      - production
    Description: Environment name
  
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
    Description: EC2 instance type
  
  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: Name of an existing EC2 KeyPair to enable SSH access

Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-0c55b159cbfafe1f0
    us-west-2:
      AMI: ami-0c55b159cbfafe1f0
    eu-west-1:
      AMI: ami-0c55b159cbfafe1f0

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-vpc'
        - Key: Environment
          Value: !Ref Environment

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-public-subnet'

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-private-subnet'

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-igw'

  VPCGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-public-rt'

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: VPCGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable

  WebSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for web servers
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
      SecurityGroupEgress:
        - IpProtocol: -1
          FromPort: 0
          ToPort: 0
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-web-sg'

  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref "AWS::Region", AMI]
      InstanceType: !Ref InstanceType
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebSecurityGroup
      KeyName: !Ref KeyName
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Hello from ${Environment}!</h1>" > /var/www/html/index.html
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-web-server'
        - Key: Environment
          Value: !Ref Environment

Outputs:
  VPCId:
    Description: The ID of the VPC
    Value: !Ref VPC
    Export:
      Name: !Sub '${Environment}-vpc-id'

  PublicSubnetId:
    Description: The ID of the public subnet
    Value: !Ref PublicSubnet
    Export:
      Name: !Sub '${Environment}-public-subnet-id'

  WebServerPublicIP:
    Description: The public IP address of the web server
    Value: !GetAtt WebServer.PublicIp
    Export:
      Name: !Sub '${Environment}-web-server-ip'
```

#### 嵌套模板
```yaml
# master.yaml - 主模板
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Master template for web application'

Parameters:
  Environment:
    Type: String
    Default: development
  
  VPCStackName:
    Type: String
    Description: Name of the VPC stack

Resources:
  VPCStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/my-templates/vpc-template.yaml
      Parameters:
        Environment: !Ref Environment
        VpcCidr: 10.0.0.0/16

  WebServerStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/my-templates/web-server-template.yaml
      Parameters:
        Environment: !Ref Environment
        VPCId: !GetAtt VPCStack.Outputs.VPCId
        PublicSubnetId: !GetAtt VPCStack.Outputs.PublicSubnetId

Outputs:
  VPCId:
    Description: The ID of the VPC
    Value: !GetAtt VPCStack.Outputs.VPCId
  
  WebServerPublicIP:
    Description: The public IP of the web server
    Value: !GetAtt WebServerStack.Outputs.WebServerPublicIP
```

#### CloudFormation宏
```yaml
# transform.yaml - 宏定义
Resources:
  MacroFunction:
    Type: AWS::Lambda::Function
    Properties:
      Handler: index.handler
      Role: !GetAtt MacroExecutionRole.Arn
      Runtime: python3.8
      Code:
        ZipFile: |
          import json
          def handler(event, context):
            fragment = event['fragment']
            if 'Type' in fragment and fragment['Type'] == 'AWS::S3::Bucket':
              # 自动添加标签
              if 'Tags' not in fragment:
                fragment['Tags'] = []
              fragment['Tags'].append({
                  'Key': 'ManagedBy',
                  'Value': 'CloudFormation'
              })
            return {
              'status': 'success',
              'fragment': fragment
            }

  MacroExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  MyMacro:
    Type: AWS::CloudFormation::Macro
    Properties:
      Name: AddTagsMacro
      FunctionName: !Ref MacroFunction

# 使用宏的模板
AWSTemplateFormatVersion: '2010-09-09'
Transform: AddTagsMacro

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket-with-tags
```

## Ansible详解

### Ansible基础概念

#### Playbook结构
```yaml
# playbook.yml - Ansible playbook
---
- name: Configure web servers
  hosts: webservers
  become: yes
  vars:
    http_port: 80
    max_clients: 200
  
  tasks:
    - name: Install Apache web server
      yum:
        name: httpd
        state: present
      when: ansible_os_family == "RedHat"
    
    - name: Install Apache web server (Debian)
      apt:
        name: apache2
        state: present
      when: ansible_os_family == "Debian"
    
    - name: Start and enable Apache service
      service:
        name: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'apache2' }}"
        state: started
        enabled: yes
    
    - name: Deploy configuration file
      template:
        src: httpd.conf.j2
        dest: /etc/httpd/conf/httpd.conf
      notify: Restart Apache
      vars:
        server_name: "{{ inventory_hostname }}"
    
    - name: Ensure document root exists
      file:
        path: /var/www/html
        state: directory
        mode: '0755'
    
    - name: Deploy index page
      copy:
        content: "<h1>Welcome to {{ inventory_hostname }}</h1>"
        dest: /var/www/html/index.html
  
  handlers:
    - name: Restart Apache
      service:
        name: "{{ 'httpd' if ansible_os_family == 'RedHat' else 'apache2' }}"
        state: restarted

- name: Configure database servers
  hosts: databases
  become: yes
  vars:
    mysql_root_password: "{{ vault_mysql_root_password }}"
  
  tasks:
    - name: Install MySQL server
      yum:
        name: mysql-server
        state: present
      when: ansible_os_family == "RedHat"
    
    - name: Start and enable MySQL service
      service:
        name: mysqld
        state: started
        enabled: yes
    
    - name: Set MySQL root password
      mysql_user:
        name: root
        password: "{{ mysql_root_password }}"
        login_unix_socket: /var/lib/mysql/mysql.sock
    
    - name: Remove anonymous MySQL users
      mysql_user:
        name: ""
        host_all: yes
        state: absent
        login_user: root
        login_password: "{{ mysql_root_password }}"
    
    - name: Remove MySQL test database
      mysql_db:
        name: test
        state: absent
        login_user: root
        login_password: "{{ mysql_root_password }}"
```

#### 角色结构
```yaml
# roles/webserver/tasks/main.yml
---
- name: Install web server packages
  package:
    name: "{{ web_server_package }}"
    state: present

- name: Start and enable web server
  service:
    name: "{{ web_server_service }}"
    state: started
    enabled: yes

- name: Deploy configuration
  template:
    src: "{{ config_template }}"
    dest: "{{ config_file }}"
  notify: Restart web server

- name: Deploy web content
  copy:
    src: index.html
    dest: "{{ document_root }}/index.html"

# roles/webserver/vars/main.yml
---
web_server_package: httpd
web_server_service: httpd
config_template: httpd.conf.j2
config_file: /etc/httpd/conf/httpd.conf
document_root: /var/www/html

# roles/webserver/handlers/main.yml
---
- name: Restart web server
  service:
    name: "{{ web_server_service }}"
    state: restarted

# roles/webserver/templates/httpd.conf.j2
ServerRoot "/etc/httpd"
Listen {{ http_port }}
ServerAdmin admin@{{ inventory_hostname }}
ServerName {{ inventory_hostname }}
DocumentRoot "{{ document_root }}"

<Directory "{{ document_root }}">
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>

# roles/webserver/files/index.html
<!DOCTYPE html>
<html>
<head>
    <title>{{ inventory_hostname }}</title>
</head>
<body>
    <h1>Welcome to {{ inventory_hostname }}</h1>
    <p>This page is managed by Ansible</p>
</body>
</html>

# 使用角色的playbook
---
- name: Configure web infrastructure
  hosts: webservers
  become: yes
  roles:
    - webserver
    - firewall
    - monitoring
```

#### 动态Inventory
```yaml
# inventory.yml - 动态inventory配置
plugin: aws_ec2
regions:
  - us-west-2
  - us-east-1
filters:
  tag:Environment:
    - production
  tag:Role:
    - webserver
 keyed_groups:
  - key: tags.Environment
    prefix: env
  - key: tags.Role
    prefix: role
compose:
  ansible_host: public_ip_address
  private_ip: private_ip_address

# 使用动态inventory的playbook
---
- name: Configure AWS instances
  hosts: "{{ target_hosts }}"
  become: yes
  vars:
    target_hosts: tag_Environment_production
  tasks:
    - name: Update system packages
      package:
        name: "*"
        state: latest
      when: ansible_os_family == "RedHat"
```

### Ansible高级特性

#### 条件和循环
```yaml
---
- name: Advanced Ansible features
  hosts: all
  become: yes
  
  tasks:
    - name: Install packages based on OS
      package:
        name: "{{ item }}"
        state: present
      loop: "{{ packages[ansible_os_family] }}"
      when: ansible_os_family in packages
    
    - name: Create multiple users
      user:
        name: "{{ item.name }}"
        groups: "{{ item.groups }}"
        shell: "{{ item.shell }}"
      loop: "{{ users }}"
      when: item.state | default('present') == 'present'
    
    - name: Configure services with conditionals
      service:
        name: "{{ item }}"
        state: started
        enabled: yes
      loop: "{{ services }}"
      when: item in ansible_facts.services
    
    - name: Generate configuration files
      template:
        src: "{{ item.template }}"
        dest: "{{ item.destination }}"
      loop: "{{ configs }}"
      notify: restart services
      when: item.enabled | default(true)
  
  vars:
    packages:
      RedHat:
        - httpd
        - php
        - mariadb
      Debian:
        - apache2
        - php
        - mariadb-server
    
    users:
      - name: alice
        groups: wheel,developers
        shell: /bin/bash
      - name: bob
        groups: developers
        shell: /bin/zsh
      - name: charlie
        groups: wheel
        shell: /bin/bash
        state: absent
    
    services:
      - httpd
      - mariadb
      - php-fpm
    
    configs:
      - template: httpd.conf.j2
        destination: /etc/httpd/conf/httpd.conf
        enabled: true
      - template: php.ini.j2
        destination: /etc/php.ini
        enabled: true
      - template: my.cnf.j2
        destination: /etc/my.cnf
        enabled: false
```

#### Ansible Vault
```bash
# 创建加密的变量文件
ansible-vault create vault.yml

# 编辑加密的变量文件
ansible-vault edit vault.yml

# 查看加密的变量文件
ansible-vault view vault.yml

# 重新加密
ansible-vault rekey vault.yml

# 使用vault的playbook
---
- name: Deploy application with secrets
  hosts: app_servers
  become: yes
  vars_files:
    - vault.yml
  vars:
    app_name: myapp
    app_version: "1.0.0"
  
  tasks:
    - name: Create application user
      user:
        name: "{{ app_name }}"
        password: "{{ vault_app_password | password_hash('sha512') }}"
        shell: /bin/bash
    
    - name: Deploy configuration with secrets
      template:
        src: app.conf.j2
        dest: "/etc/{{ app_name }}/app.conf"
        mode: '0600'
        owner: "{{ app_name }}"
        group: "{{ app_name }}"
      vars:
        db_password: "{{ vault_db_password }}"
        api_key: "{{ vault_api_key }}"
```

## Pulumi详解

### Pulumi基础概念

#### Python Pulumi示例
```python
# __main__.py - Pulumi Python程序
import pulumi
import pulumi_aws as aws

# 创建VPC
vpc = aws.ec2.Vpc("main-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": "main-vpc",
        "Environment": pulumi.get_stack(),
    }
)

# 创建子网
public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone=aws.get_availability_zones().names[0],
    map_public_ip_on_launch=True,
    tags={
        "Name": "public-subnet",
    }
)

private_subnet = aws.ec2.Subnet("private-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone=aws.get_availability_zones().names[0],
    tags={
        "Name": "private-subnet",
    }
)

# 创建安全组
security_group = aws.ec2.SecurityGroup("web-sg",
    description="Security group for web servers",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={
        "Name": "web-sg",
    }
)

# 创建EC2实例
instance = aws.ec2.Instance("web-server",
    ami="ami-0c55b159cbfafe1f0",
    instance_type="t3.micro",
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "web-server",
    },
    user_data="""#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from Pulumi!</h1>" > /var/www/html/index.html
"""
)

# 导出值
pulumi.export("vpc_id", vpc.id)
pulumi.export("public_subnet_id", public_subnet.id)
pulumi.export("instance_public_ip", instance.public_ip)
pulumi.export("instance_public_dns", instance.public_dns)
```

#### TypeScript Pulumi示例
```typescript
// index.ts - Pulumi TypeScript程序
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// 创建配置
const config = new pulumi.Config();
const environment = config.get("environment") || "development";
const instanceType = config.get("instanceType") || "t3.micro";

// 创建VPC
const vpc = new aws.ec2.Vpc("main-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
    tags: {
        Name: "main-vpc",
        Environment: environment,
    },
});

// 创建子网
const publicSubnet = new aws.ec2.Subnet("public-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: aws.getAvailabilityZones().then(azs => azs.names[0]),
    mapPublicIpOnLaunch: true,
    tags: {
        Name: "public-subnet",
    },
});

const privateSubnet = new aws.ec2.Subnet("private-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.2.0/24",
    availabilityZone: aws.getAvailabilityZones().then(azs => azs.names[0]),
    tags: {
        Name: "private-subnet",
    },
});

// 创建安全组
const securityGroup = new aws.ec2.SecurityGroup("web-sg", {
    description: "Security group for web servers",
    vpcId: vpc.id,
    ingress: [
        {
            protocol: "tcp",
            fromPort: 80,
            toPort: 80,
            cidrBlocks: ["0.0.0.0/0"],
        },
        {
            protocol: "tcp",
            fromPort: 443,
            toPort: 443,
            cidrBlocks: ["0.0.0.0/0"],
        },
    ],
    egress: [
        {
            protocol: "-1",
            fromPort: 0,
            toPort: 0,
            cidrBlocks: ["0.0.0.0/0"],
        },
    ],
    tags: {
        Name: "web-sg",
    },
});

// 创建EC2实例
const instance = new aws.ec2.Instance("web-server", {
    ami: "ami-0c55b159cbfafe1f0",
    instanceType: instanceType,
    subnetId: publicSubnet.id,
    vpcSecurityGroupIds: [securityGroup.id],
    tags: {
        Name: "web-server",
        Environment: environment,
    },
    userData: `#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from Pulumi!</h1>" > /var/www/html/index.html
`,
});

// 导出值
export const vpcId = vpc.id;
export const publicSubnetId = publicSubnet.id;
export const instancePublicIp = instance.publicIp;
export const instancePublicDns = instance.publicDns;
```

#### 组件化设计
```python
# components/vpc.py - VPC组件
import pulumi
import pulumi_aws as aws

class VpcComponent:
    def __init__(self, name: str, cidr_block: str, availability_zones: list, tags: dict = None):
        self.name = name
        self.cidr_block = cidr_block
        self.availability_zones = availability_zones
        self.tags = tags or {}
        
        # 创建VPC
        self.vpc = aws.ec2.Vpc(f"{name}-vpc",
            cidr_block=cidr_block,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags={**self.tags, "Name": f"{name}-vpc"}
        )
        
        # 创建子网
        self.public_subnets = []
        self.private_subnets = []
        
        for i, az in enumerate(availability_zones):
            # 公有子网
            public_subnet = aws.ec2.Subnet(f"{name}-public-{i}",
                vpc_id=self.vpc.id,
                cidr_block=self._get_subnet_cidr(i, 0),
                availability_zone=az,
                map_public_ip_on_launch=True,
                tags={**self.tags, "Name": f"{name}-public-{i}"}
            )
            self.public_subnets.append(public_subnet)
            
            # 私有子网
            private_subnet = aws.ec2.Subnet(f"{name}-private-{i}",
                vpc_id=self.vpc.id,
                cidr_block=self._get_subnet_cidr(i, 1),
                availability_zone=az,
                tags={**self.tags, "Name": f"{name}-private-{i}"}
            )
            self.private_subnets.append(private_subnet)
        
        # 创建互联网网关
        self.internet_gateway = aws.ec2.InternetGateway(f"{name}-igw",
            vpc_id=self.vpc.id,
            tags={**self.tags, "Name": f"{name}-igw"}
        )
        
        # 创建NAT网关
        self.nat_gateway = aws.ec2.NatGateway(f"{name}-nat",
            allocation_id=aws.eip.Eip(f"{name}-eip",
                vpc=True,
                tags={**self.tags, "Name": f"{name}-eip"}
            ).id,
            subnet_id=self.public_subnets[0].id,
            tags={**self.tags, "Name": f"{name}-nat"}
        )
        
        # 创建路由表
        self.public_route_table = aws.ec2.RouteTable(f"{name}-public-rt",
            vpc_id=self.vpc.id,
            routes=[
                aws.ec2.RouteTableRouteArgs(
                    cidr_block="0.0.0.0/0",
                    gateway_id=self.internet_gateway.id,
                )
            ],
            tags={**self.tags, "Name": f"{name}-public-rt"}
        )
        
        self.private_route_table = aws.ec2.RouteTable(f"{name}-private-rt",
            vpc_id=self.vpc.id,
            routes=[
                aws.ec2.RouteTableRouteArgs(
                    cidr_block="0.0.0.0/0",
                    nat_gateway_id=self.nat_gateway.id,
                )
            ],
            tags={**self.tags, "Name": f"{name}-private-rt"}
        )
        
        # 关联路由表
        for i, subnet in enumerate(self.public_subnets):
            aws.ec2.RouteTableAssociation(f"{name}-public-rt-assoc-{i}",
                subnet_id=subnet.id,
                route_table_id=self.public_route_table.id
            )
        
        for i, subnet in enumerate(self.private_subnets):
            aws.ec2.RouteTableAssociation(f"{name}-private-rt-assoc-{i}",
                subnet_id=subnet.id,
                route_table_id=self.private_route_table.id
            )
    
    def _get_subnet_cidr(self, index: int, type: int) -> str:
        """生成子网CIDR"""
        base_octets = self.cidr_block.split('.')
        if type == 0:  # 公有子网
            return f"{base_octets[0]}.{base_octets[1]}.{index + 1}.0/24"
        else:  # 私有子网
            return f"{base_octets[0]}.{base_octets[1]}.{index + 10}.0/24"

# 使用组件
# __main__.py
import pulumi
from components.vpc import VpcComponent

# 获取配置
config = pulumi.Config()
environment = config.get("environment") || "development"

# 获取可用区
availability_zones = aws.get_availability_zones().names

# 创建VPC组件
vpc_component = VpcComponent(
    name=f"{environment}-vpc",
    cidr_block="10.0.0.0/16",
    availability_zones=availability_zones[:2],
    tags={"Environment": environment}
)

# 导出值
pulumi.export("vpc_id", vpc_component.vpc.id)
pulumi.export("public_subnet_ids", pulumi.Output.all(*[subnet.id for subnet in vpc_component.public_subnets]))
pulumi.export("private_subnet_ids", pulumi.Output.all(*[subnet.id for subnet in vpc_component.private_subnets]))
```

## IaC最佳实践

### 代码组织结构
```
project-root/
├── environments/
│   ├── development/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── security/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── compute/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── scripts/
│   ├── deploy.sh
│   ├── destroy.sh
│   └── validate.sh
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── architecture.md
│   └── operations.md
├── .gitignore
├── README.md
└── Makefile
```

### 安全最佳实践
```hcl
# security.tf - 安全配置示例
# 使用IAM角色而不是访问密钥
resource "aws_iam_role" "ec2_role" {
  name = "ec2-instance-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  }
}

# 最小权限原则
resource "aws_iam_policy" "ec2_policy" {
  name = "ec2-instance-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect = "Allow"
        Resource = "arn:aws:s3:::my-bucket/*"
      }
    ]
  })
}

# 加密所有存储
resource "aws_ebs_volume" "encrypted" {
  availability_zone = aws_instance.web.availability_zone
  size              = 10
  encrypted         = true
  kms_key_id        = aws_kms_key.example.arn
}

# 使用安全组而不是开放端口
resource "aws_security_group" "restricted" {
  name        = "restricted-sg"
  description = "Restricted security group"
  
  # 只允许必要的端口
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }
  
  # 明确拒绝不必要的流量
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### 成本优化实践
```hcl
# cost-optimization.tf - 成本优化示例
# 使用Spot实例
resource "aws_spot_instance_request" "web" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t3.micro"
  spot_price    = "0.02"
  spot_type     = "persistent"
  
  tags = {
    Name = "spot-web-server"
  }
}

# 使用自动缩放
resource "aws_autoscaling_group" "web" {
  vpc_zone_identifier       = module.vpc.public_subnet_ids
  desired_capacity          = 2
  max_size                  = 6
  min_size                  = 2
  health_check_grace_period = 300
  health_check_type         = "EC2"
  
  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }
}

# 使用生命周期策略
resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs-bucket"
  
  lifecycle_rule {
    id     = "log_lifecycle"
    enabled = true
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 60
      storage_class = "GLACIER"
    }
    
    transition {
      days          = 180
      storage_class = "DEEP_ARCHIVE"
    }
    
    expiration {
      days = 365
    }
  }
}
```

## 参考资源

### 官方文档
- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [Ansible Documentation](https://docs.ansible.com/)
- [Pulumi Documentation](https://www.pulumi.com/docs/)

### 学习资源
- [Terraform Tutorial](https://learn.hashicorp.com/terraform)
- [AWS CloudFormation Getting Started](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/GettingStarted.html)
- [Ansible User Guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Pulumi Getting Started](https://www.pulumi.com/get-started)

### 社区资源
- [Terraform Registry](https://registry.terraform.io/)
- [AWS Quick Start](https://aws.amazon.com/quickstart/)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Pulumi Registry](https://www.pulumi.com/registry)

### 最佳实践指南
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/aws/guides/best-practices/index.html)
- [CloudFormation Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [IaC Security Guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Infrastructure_as_Code_Security_Cheat_Sheet.html)
