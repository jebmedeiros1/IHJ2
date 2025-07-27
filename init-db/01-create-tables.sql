-- Script de inicialização do banco de dados IHJ
-- Este script deve ser executado no PostgreSQL existente

-- Conectar ao banco ihj_database (será criado se não existir)
-- CREATE DATABASE ihj_database; -- Execute manualmente se necessário

-- Usar o banco ihj_database
\c ihj_database;

-- Criar tabela de equipamentos (exemplo baseado nos dados originais)
CREATE TABLE IF NOT EXISTS equipamentos (
    id SERIAL PRIMARY KEY,
    equipamento VARCHAR(50) NOT NULL UNIQUE,
    localizacao VARCHAR(100),
    denominacao_localizacao VARCHAR(200),
    material VARCHAR(200),
    classe VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de características dos equipamentos
CREATE TABLE IF NOT EXISTS caracteristicas (
    id SERIAL PRIMARY KEY,
    equipamento_id INTEGER REFERENCES equipamentos(id),
    nome_caracteristica VARCHAR(100) NOT NULL,
    valor_caracteristica VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_equipamentos_equipamento ON equipamentos(equipamento);
CREATE INDEX IF NOT EXISTS idx_equipamentos_classe ON equipamentos(classe);
CREATE INDEX IF NOT EXISTS idx_caracteristicas_equipamento_id ON caracteristicas(equipamento_id);
CREATE INDEX IF NOT EXISTS idx_caracteristicas_nome ON caracteristicas(nome_caracteristica);

-- Inserir dados de exemplo (baseados no arquivo original)
INSERT INTO equipamentos (equipamento, localizacao, denominacao_localizacao, material, classe) VALUES
('MTE01241', 'LOC001', 'Área de Produção 1', 'Bomba Centrífuga', 'Bombas'),
('MTE01242', 'LOC002', 'Área de Produção 2', 'Motor Elétrico', 'Motores'),
('MTE01243', 'LOC003', 'Área de Produção 3', 'Válvula de Controle', 'Válvulas'),
('MTE01244', 'LOC004', 'Área de Produção 4', 'Compressor', 'Compressores'),
('MTE01245', 'LOC005', 'Área de Produção 5', 'Trocador de Calor', 'Trocadores de Calor')
ON CONFLICT (equipamento) DO NOTHING;

-- Inserir características de exemplo
INSERT INTO caracteristicas (equipamento_id, nome_caracteristica, valor_caracteristica) VALUES
(1, 'Potência', '100HP'),
(1, 'Vazão', '500 L/min'),
(1, 'Pressão', '10 bar'),
(1, 'Material', 'Aço Carbono'),
(2, 'Potência', '150HP'),
(2, 'Rotação', '1800 RPM'),
(2, 'Tensão', '380V'),
(2, 'Material', 'Ferro Fundido'),
(3, 'Diâmetro', '4 polegadas'),
(3, 'Pressão', '16 bar'),
(3, 'Material', 'Aço Inox'),
(3, 'Tipo', 'Globo'),
(4, 'Potência', '200HP'),
(4, 'Pressão', '8 bar'),
(4, 'Vazão', '1000 m³/h'),
(4, 'Material', 'Aço Carbono'),
(5, 'Área', '50 m²'),
(5, 'Pressão', '12 bar'),
(5, 'Material', 'Aço Inox'),
(5, 'Tipo', 'Casco e Tubo')
ON CONFLICT DO NOTHING;

-- Criar função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar triggers para atualizar timestamp automaticamente
DROP TRIGGER IF EXISTS update_equipamentos_updated_at ON equipamentos;
CREATE TRIGGER update_equipamentos_updated_at BEFORE UPDATE ON equipamentos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_caracteristicas_updated_at ON caracteristicas;
CREATE TRIGGER update_caracteristicas_updated_at BEFORE UPDATE ON caracteristicas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

