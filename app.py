from flask import Flask, request, jsonify
import sentry_sdk
from discord_webhook import DiscordWebhook, DiscordEmbed
import requests

app = Flask(__name__)

sentry_sdk.init(
    dsn="https://c241a7e3a3eba48d9f94edd4ab66de72@o4506746068140032.ingest.sentry.io/4506746068336640",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

jira_url = 'https://amplisoftware.atlassian.net/browse'

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    github_event = request.headers.get('X-GitHub-Event')

    github_payload = request.json

    webhook_url = 'https://discord.com/api/webhooks/1196531971782868995/I3b2Zfzn_wW9W9TUfQVdJmKtaqb3FSfBrPRw7BzreOYMWwjZqaDV1-iUhzY_99AeuHt-'

    if github_event == 'ping':
        return jsonify({'message': 'Pong!'}), 200

    elif github_event == 'push':
    # Criar o embed para o Discord
        # Extrair informações relevantes do payload do GitHub
        repository_name = github_payload['repository']['full_name']
        branch_name = github_payload['ref'].split('refs/heads/')[-1]
        # explodindo variaveis da branch com - para pegar a primeira e a segunda parte
        branch_card = branch_name.split('/')[-1].split('-')
        if len(branch_card) >= 2:
            branch_card = branch_card[0]+'-'+branch_card[1]
            card_url = jira_url +'/'+ branch_card
        else:
            branch_card = branch_card[0]
            card_url = ''
        author_api_url = github_payload['sender']['url']
        author_data = requests.get(author_api_url).json()
        author_name = author_data['name']
        author_user = github_payload['sender']['login']
        author_avatar_url = github_payload['sender']['avatar_url']
        author_url = github_payload['sender']['html_url']
        branch_url = github_payload['repository']['html_url'] + '/commits/' + branch_name

        embed = DiscordEmbed(
            title=f'⬆️ {branch_name}',
            url=branch_url,
            description=f'[`Clique para abrir o card!`]({card_url})',
            color='9900ff'
        )
        embed.set_author(
            name=f'{author_name} - @{author_user}',
            icon_url=author_avatar_url,
            url=author_url
        )
        # Adicionar campos para os commits
        for commit in github_payload['commits']:
            # Adicionar o campo para os arquivos deste commit
            commit_message = commit['message']
            commit_id = commit['id'][:7]  # Pegar apenas os primeiros 7 caracteres do commit_id
            commit_url = commit['url']
            commit_changes = {
                'Arquivos adicionados': commit['added'],
                'Arquivos alterados': commit['modified'],
                'Arquivos excluídos': commit['removed']
            }

            # Inicialize uma lista para armazenar os campos divididos
            divided_fields = []

            # Inicialize uma variável para armazenar o texto atual acumulado
            current_text = ""

            # Itere sobre os tipos de alterações e os arquivos correspondentes
            for change_type, files in commit_changes.items():
                for file in files:
                    # Construa a linha de texto para o arquivo atual
                    if change_type == 'Arquivos adicionados':
                        line = f"\u001b[0;32m+ {file}\n"
                    elif change_type == 'Arquivos alterados':
                        line = f"\u001b[0;33m  {file}\n"
                    elif change_type == 'Arquivos excluídos':
                        line = f"\u001b[0;31m- {file}\n"

                    # Verifique se a adição da linha excederá o limite de caracteres
                    if len(current_text) + len(line) > 800:
                        # Se sim, adicione o campo atual à lista de campos divididos
                        divided_fields.append(current_text)
                        # Reinicie o texto atual com a linha atual
                        current_text = line
                    else:
                        # Se não, adicione a linha ao texto atual
                        current_text += line

            # Adicione o texto restante ao último campo dividido
            divided_fields.append(current_text)

            # Adicione cada campo dividido como um novo campo no embed
            for index, text in enumerate(divided_fields):
                if index == 0:
                    embed.add_embed_field(name=f"Commit ➡️ {commit_message}", value=f'[`{commit_id}`]({commit_url})\n```ansi\n{text}```', inline=False)
                else:
                # Adicione o campo ao embed
                    embed.add_embed_field(name=f"Commit ➡️ {commit_message} (Parte {index+1})", value=f'[`{commit_id}`]({commit_url})\n```ansi\n{text}```', inline=False)


    elif github_event == 'create':
        # Adicionar campo para a criação do branch
        repository_name = github_payload['repository']['full_name']
        branch_name = github_payload['ref']
        branch_url = github_payload['repository']['html_url'] + '/tree/' + branch_name

        branch_id = branch_name.split('refs/heads/')[-1].split('/')[-1].split('-')
        branch_id = branch_id[0]+'-'+branch_name[1]
        card_url = jira_url +'/'+ branch_id

        author_api_url = github_payload['sender']['url']
        author_data = requests.get(author_api_url).json()
        author_name = author_data['name']
        author_user = github_payload['sender']['login']
        author_avatar_url = github_payload['sender']['avatar_url']
        author_url = github_payload['sender']['html_url']

        embed = DiscordEmbed(
            title=f'🆕 {repository_name}',
            url=branch_url,
            color='9900ff'
        )
        embed.set_author(
            name=f"{author_name} - @{author_user}",
            icon_url=author_avatar_url,
            url=author_url
        )

        embed.add_embed_field(name=branch_name, value="```ansi\n✅ \u001b[0;35mNova branch criada com sucesso!\n```", inline=False)
        embed.add_embed_field(name='', value=f"[`Clique para abrir o card!`]({card_url})", inline=False)

    elif github_event == 'delete':
        # Adicionar campo para a criação do branch
        repository_name = github_payload['repository']['full_name']
        branch_name = github_payload['ref']
        branch_url = github_payload['repository']['html_url']
        author_name = github_payload['sender']['login']
        author_avatar_url = github_payload['sender']['avatar_url']
        author_url = github_payload['sender']['html_url']

        embed = DiscordEmbed(
            title=f'{repository_name}',
            url=branch_url,
            color='9900ff'
        )
        embed.set_author(
            name=author_name,
            icon_url=author_avatar_url,
            url=author_url
        )

        embed.add_embed_field(name=branch_name, value="```ansi\n🚨 \u001b[0;35mBranch deletada com sucesso!\n```", inline=False)

    elif github_event == 'pull_request':
        webhook_url = 'https://discord.com/api/webhooks/1196531363868848208/Hu2pY0EfJP7knLd1h824DOBvxOc_iSM4ffPMdSYvm5vzNrXlvRMbbjXTYIqggOEJg8b1'

        # Adicionar campo para a criação do branch
        pull_number = github_payload['number']
        pull_details = github_payload['pull_request']['title']
        pull_url = github_payload['pull_request']['html_url']
        pull_message = github_payload['pull_request']['body']

        repository_name = github_payload['repository']['full_name']

        reviewers = github_payload['pull_request']['requested_reviewers']
        branch_url = github_payload['pull_request']['html_url']
        author_name = github_payload['sender']['login']
        author_avatar_url = github_payload['sender']['avatar_url']
        author_url = github_payload['sender']['html_url']

        embed = DiscordEmbed(
            title=f'⚛️{repository_name}',
            url=branch_url,
            color='9900ff'
        )
        embed.set_author(
            name=author_name,
            icon_url=author_avatar_url,
            url=author_url
        )

        if github_payload['action'] == 'opened':
            embed.add_embed_field(name=f'Nova PR: {pull_details} - Nº{pull_number}', value=f"```ansi\n🔀 \u001b[0;35mPull Request criado com sucesso!\n```\n[`Acesse aqui!`]({pull_url})", inline=False)
            if pull_message:
                embed.add_embed_field(name='Mensagem', value=f"```\n{pull_message}\n```", inline=False)

            reviewer_text = ''
            for reviewer in reviewers:

                reviewer_text += f'@{reviewer["login"]}\n'

            embed.add_embed_field(name='Revisores solicitados', value=f"```\n{reviewer_text}\n```", inline=False)

        elif github_payload['action'] == 'closed':
            embed.add_embed_field(name=f'PR: {pull_details} - Nº{pull_number}', value=f"```ansi\n🚨 \u001b[0;35mPull Request fechado com sucesso!\n```\n[`Acesse aqui!`]({pull_url})", inline=False)
        else:
            return jsonify({'message': 'Evento não suportado!'}), 400
        
    elif github_event == 'pull_request_review':
        webhook_url = 'https://discord.com/api/webhooks/1196531363868848208/Hu2pY0EfJP7knLd1h824DOBvxOc_iSM4ffPMdSYvm5vzNrXlvRMbbjXTYIqggOEJg8b1'

        pull_url = github_payload['pull_request']['html_url']
        pull_number = github_payload['pull_request']['number']
        pull_details = github_payload['pull_request']['title']
        pull_message = github_payload['pull_request']['body']
        repository_name = github_payload['repository']['full_name']

        branch_name = github_payload['pull_request']['head']['ref']
        branch_url = github_payload['repository']['html_url'] + '/tree/' + branch_name

        author_url = github_payload['sender']['url']
        author_data = requests.get(author_url).json()
        author_name = author_data['name']
        author_user = github_payload['sender']['login']
        author_avatar_url = github_payload['sender']['avatar_url']

        review_author = github_payload['review']['user']['login']
        review_author_url = github_payload['review']['user']['url']
        review_author_name = requests.get(review_author_url).json()['name']
        review_state = github_payload['review']['state']
        review_body = github_payload['review']['body']

        embed = DiscordEmbed(
            title=f'⚛️{repository_name}',
            url=pull_url,
            color='9900ff'
        )
        embed.set_author(
            name=author_name,
            icon_url=author_avatar_url,
            url=author_url
        )
        if review_state == 'approved':
            embed.add_embed_field(name=f'PR: {pull_details} - Nº{pull_number}', value=f"```ansi\n✅ \u001b[0;35mPR aprovada!\n```\n[`Acesse aqui!`]({pull_url})", inline=False)
        elif review_state == 'changes_requested':
            embed.add_embed_field(name=f'PR: {pull_details} - Nº{pull_number}', value=f"```ansi\n🚨 \u001b[0;35mAlterações solicitadas!\n```\n[`Acesse aqui!`]({pull_url})", inline=False)
        elif review_state == 'commented':
            embed.add_embed_field(name=f'PR: {pull_details} - Nº{pull_number}', value=f"```ansi\n💬 \u001b[0;35mComentário adicionado!\n```\n[`Acesse aqui!`]({pull_url})", inline=False)
        elif review_state == 'dismissed':
            embed.add_embed_field(name=f'PR: {pull_details} - Nº{pull_number}', value=f"```ansi\n🚫 \u001b[0;35mPR rejeitada!\n```\n[`Acesse aqui!`]({pull_url})", inline=False)
        else:
            return jsonify({'message': 'Evento não suportado!'}), 400
        
        # Quem fez a revisão e seu comentário sem set_author
        embed.add_embed_field(name=f'Revisor: {review_author_name} - @{review_author}', value=f"```ansi\n{review_body}\n```", inline=False)
    else:
        return jsonify({'message': 'Evento não suportado!'}), 400
    # Adicionar o timestamp ao embed
    embed.set_timestamp()

    webhook = DiscordWebhook(url=webhook_url)
    webhook.username = 'Migradeiro Bot'
    webhook.avatar_url = 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/ca3c0184-a1bc-4cf1-8e61-2c0caa693056/dfod5oa-b33b2795-ef4e-4e09-8761-a48d3cbb3a78.png/v1/fit/w_512,h_512,q_70,strp/discord_avatar_512_vgtn8_by_mrbluetuxedo_dfod5oa-375w-2x.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NTEyIiwicGF0aCI6IlwvZlwvY2EzYzAxODQtYTFiYy00Y2YxLThlNjEtMmMwY2FhNjkzMDU2XC9kZm9kNW9hLWIzM2IyNzk1LWVmNGUtNGUwOS04NzYxLWE0OGQzY2JiM2E3OC5wbmciLCJ3aWR0aCI6Ijw9NTEyIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.UBnr85mLgr78iOoTpfLS9fHuTDdxpCP54kG6gchiBhw'


    # Adicionar o embed ao webhook
    webhook.add_embed(embed)

    # Enviar o webhook com todos os commits
    response = webhook.execute(remove_embeds=False)

    data_json = response

    return jsonify({'message': f'Webhook recebido com sucesso!{data_json}'}), 200

if __name__ == '__main__':
    app.run(debug=True)
