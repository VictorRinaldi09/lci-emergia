CREATE DATABASE IF NOT EXISTS calculadora_emergia;
USE calculadora_emergia;

-- Tabela de Usuários (Confidencialidade)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    nivel_acesso ENUM('admin', 'usuario') DEFAULT 'usuario'
);

-- Tabela LCI de Carros Elétricos (Integridade)
CREATE TABLE IF NOT EXISTS fatores_emergia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item VARCHAR(100) NOT NULL,
    transformidade DOUBLE NOT NULL, -- Ex: 2.0E12
    unidade VARCHAR(20)             -- Ex: joule, kg
);

-- Tabela de Auditoria (Monitoramento)
CREATE TABLE IF NOT EXISTS logs_acesso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    acao VARCHAR(255),
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);