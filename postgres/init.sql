CREATE TABLE radcheck (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    attribute VARCHAR(64) NOT NULL,
    op VARCHAR(2) NOT NULL DEFAULT ':=',
    value VARCHAR(253) NOT NULL
);


CREATE TABLE radreply (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    attribute VARCHAR(64) NOT NULL,
    op VARCHAR(2) NOT NULL DEFAULT ':=',
    value VARCHAR(253) NOT NULL
);

CREATE TABLE radusergroup (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    groupname VARCHAR(64) NOT NULL,
    priority INTEGER NOT NULL DEFAULT 1
);



CREATE TABLE radgroupreply (
    id SERIAL PRIMARY KEY,
    groupname VARCHAR(64) NOT NULL,
    attribute VARCHAR(64) NOT NULL,
    op VARCHAR(2) NOT NULL DEFAULT ':=',
    value VARCHAR(253) NOT NULL
);


CREATE TABLE radacct (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    nasipaddress INET, 
    acctsessionid VARCHAR(64),
    acctstarttime TIMESTAMP,
    acctstoptime TIMESTAMP,
    acctsessiontime BIGINT DEFAULT 0,
    acctinputoctets BIGINT DEFAULT 0,
    acctoutputoctets  BIGINT DEFAULT 0,
    acctterminatecause VARCHAR(32),
    callingstationid VARCHAR(50),
    framedipaddress INET
);


-- Test kullanıcıları
INSERT INTO radcheck (username, attribute, op, value) VALUES
('admin_user', 'Bcrypt-Password', ':=', '$2b$12$vo05iK9wscu65Zidpv7xR.EHftIp3eJSOeqlM3XGHuwuqL7k9DXHy'),
('employee_user', 'Bcrypt-Password', ':=', '$2b$12$gEWdiV5j0YFjciNtuWbr4uLp.LUxXEgnG03o70Kq33ufe8ABsn2LG'),
('guest_user', 'Bcrypt-Password', ':=', '$2b$12$FhZZFchIL1WGXCBEPkGJ4uzrri2ysw/93nXRZaiRkMljNibdU.WbG');

-- Kullanıcı grup atamaları
INSERT INTO radusergroup (username, groupname, priority) VALUES
('admin_user', 'admin', 1),
('employee_user', 'employee', 1),
('guest_user', 'guest', 1),
('chap_user', 'employee', 1);

-- VLAN atamaları
INSERT INTO radgroupreply (groupname, attribute, op, value) VALUES
('admin', 'Tunnel-Type', ':=', 'VLAN'),
('admin', 'Tunnel-Medium-Type', ':=', 'IEEE-802'),
('admin', 'Tunnel-Private-Group-Id', ':=', '10'),
('employee', 'Tunnel-Type', ':=', 'VLAN'),
('employee', 'Tunnel-Medium-Type', ':=', 'IEEE-802'),
('employee', 'Tunnel-Private-Group-Id', ':=', '20'),
('guest', 'Tunnel-Type', ':=', 'VLAN'),
('guest', 'Tunnel-Medium-Type', ':=', 'IEEE-802'),
('guest', 'Tunnel-Private-Group-Id', ':=', '30');


-- MAB guest/fixed
INSERT INTO radcheck (username, attribute, op, value) VALUES
('AA:BB:CC:DD:EE:FF', 'MAB-Password', ':=', 'mab-secret');

-- CHAP için 
INSERT INTO radcheck (username, attribute, op, value) VALUES
('chap_user', 'Cleartext-Password', ':=', 'chap123');

-- Kullanıcıya özel attributes (radreply)
INSERT INTO radreply (username, attribute, op, value) VALUES
('admin_user', 'Framed-IP-Address', ':=', '192.168.1.10');

-- Performans index'leri
CREATE INDEX idx_radcheck_username ON radcheck(username);
CREATE INDEX idx_radusergroup_username ON radusergroup(username);
CREATE INDEX idx_radacct_username ON radacct(username);
CREATE INDEX idx_radacct_sessionid ON radacct(acctsessionid);
