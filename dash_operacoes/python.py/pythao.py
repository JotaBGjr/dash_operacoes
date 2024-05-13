import mysql.connector
import matplotlib.pyplot as plt

# Estabelecer conexão com o banco de dados

def connect_to_database():
    try:
        global conexao
        conexao = mysql.connector.connect(
            host="iot-laager.c3wepnzq2di2.us-east-1.rds.amazonaws.com",
            user="jorge",
            password="devjorge",
            database="DLAAGERIOT"
            )
            # Verificando a conexão ao banco de dados;
        if conexao.is_connected():
            print("Conexão ao DLAAGERIOT bem sucedida")
            
            # CONSULTA
            slct_sla_projetos = """
                SELECT c.name as Compania,
                    bu.name as unidade_de_negocio,
                    bu.company_id, NOW() data_da_consulta,
                    count(m.device_serial_number) as numero_de_ativos,
                    sum(case when datediff(now(),m.last_read_at) <= 1 then 1 else 0 end) as ult_24hs_tranmiss,
                    sum(case when datediff(now() ,m.last_read_at) >= 2 then 1 else 0 end) as Pontos_verificar,
                    sum(case when datediff(now(),m.last_read_at) <= 1 then 1 else 0 end) / count(m.device_serial_number) as SLA
                FROM companies c
                    join business_units bu on c.id = bu.company_id
                    join commercial_services cs on bu.id = cs.business_unit_id
                    join residences r on cs.id = r.commercial_service_id
                    join meters m on r.id = m.residence_id
                WHERE 
                    c.name  in ('Grupo GPS','Algar - Águas de Joinville','SGU - SANASA','Ultragaz','Supergasbras','Riviera de São Lourenço','BBP Sanipark')
                    and r.status ='ACTIVATED'
                    group by c.name, bu.name, bu.company_id
                    order by c.name, bu.name;
            """
            # cursor para executar a consulta
            cursor = conexao.cursor()
            # executando a consulta
            cursor.execute(slct_sla_projetos)
            resultado_sla = cursor.fetchall()

            # imprimir os resultados
            # for resultado_sla in resultado_sla:
              # print(resultado_sla)
            cursor.close()
            conexao.close()
            print("Conexão encerrada.")
            print('starting the code...')

            # Listas para armazenar os valores do gráfico 1
            unidade_negocio = [resultado_sla[1] for resultado_sla in resultado_sla]
            ult_24hs_tranmiss = [resultado_sla[5] for resultado_sla in resultado_sla]
            pontos_verificar = [resultado_sla[6] for resultado_sla in resultado_sla]
            # criando gráfico de barras
            plt.figure(figsize=(10,6))
            bars = plt.bar(unidade_negocio,ult_24hs_tranmiss, color='blue',label='Últimas 24hs')
            plt.bar(unidade_negocio,pontos_verificar,color='orange',label='Pontos sem transmissão', alpha=0.7)

            # rótulos de dados da barra
            for bar in bars:
              yval = bar.get_height()
              plt.text(bar.get_x() + bar.get_width()/2.0, yval, round(yval,2),va='bottom')
            
            
            # adicionar rótulos e títulos ao gráfico
            
            plt.xlabel('Unidade de negócio')
            plt.ylabel('Quantidade')
            plt.title('Últimas 24h vs. pontos sem transm por Unidade de negócio')
            plt.xticks(rotation=45, ha='right')
            plt.legend()


            # Mostrar o histograma
            plt.tight_layout()
            plt.show()
            

    except mysql.connector.Error as erro:
        print("Erro ao conectar ao MySQL:", erro)
connect_to_database()
