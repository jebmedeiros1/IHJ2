import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search, BarChart3, ArrowRight } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Busca por Características',
      description: 'Filtre equipamentos com base em suas características específicas. Selecione classes e aplique filtros para encontrar os equipamentos que atendem aos seus critérios.',
      icon: Search,
      href: '/dashboard/caracteristicas',
      color: 'bg-blue-500'
    },
    {
      title: 'Análise de Similaridade',
      description: 'Encontre equipamentos similares a um equipamento específico. Analise características em comum e identifique alternativas ou equipamentos relacionados.',
      icon: BarChart3,
      href: '/dashboard/similaridade',
      color: 'bg-green-500'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          Bem-vindo ao sistema de busca de equipamentos. Escolha uma das opções abaixo para começar.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Card key={feature.title} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <div className={`p-2 rounded-lg ${feature.color}`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </div>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={() => navigate(feature.href)}
                  className="w-full"
                  variant="outline"
                >
                  Acessar
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Informações do Sistema</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h4 className="font-semibold mb-2">Funcionalidades Principais:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Busca avançada por características</li>
                <li>• Análise de similaridade entre equipamentos</li>
                <li>• Visualização de dados em tabelas dinâmicas</li>
                <li>• Interface responsiva e intuitiva</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Como usar:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Use o menu lateral para navegar</li>
                <li>• Selecione classes e características para filtrar</li>
                <li>• Digite códigos de equipamentos para análise</li>
                <li>• Visualize resultados em formato de tabela</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

