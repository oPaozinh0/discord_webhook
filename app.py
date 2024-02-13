from flask import Flask, request, jsonify
from discord_webhook import DiscordWebhook, DiscordEmbed
import requests

app = Flask(__name__)

jira_url = 'https://amplisoftware.atlassian.net/browse'

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    github_event = request.headers.get('X-GitHub-Event')

    github_payload = request.json

    webhook_url = 'https://discordapp.com/api/webhooks/1204507570979475496/ox5XYN67s1bBfn1zUUYgYRGnC9UgFhVRPIFES52wTykAfryu0jmACzOVJ3z64Xkic9vT'


    if github_event == 'ping':
        return jsonify({'message': 'Pong!'}), 200

    elif github_event == 'push':
    # Criar o embed para o Discord
        # Extrair informações relevantes do payload do GitHub
        repository_name = github_payload['repository']['full_name']
        branch_name = github_payload['ref'].split('refs/heads/')[-1]
        # explodindo variaveis da branch com / e pegar a ultima parte
        branch_card = branch_name.split('/')[-1].split('-')
        # explodindo variaveis da branch com - para pegar a primeira e a segunda parte
        branch_card = branch_card[0]+'-'+branch_card[1]
        card_url = jira_url +'/'+ branch_card
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

        branch_name = branch_name.split('refs/heads/')[-1].split('/')[-1].split('-')
        branch_name = branch_name[0]+'-'+branch_name[1]
        card_url = jira_url +'/'+ branch_name

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
        webhook_url = 'https://discordapp.com/api/webhooks/1204507570979475496/ox5XYN67s1bBfn1zUUYgYRGnC9UgFhVRPIFES52wTykAfryu0jmACzOVJ3z64Xkic9vT'

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
    # Adicionar o timestamp ao embed
    embed.set_timestamp()

    webhook = DiscordWebhook(url=webhook_url)


    # Adicionar o embed ao webhook
    webhook.add_embed(embed)

    # Enviar o webhook com todos os commits
    response = webhook.execute(remove_embeds=False)

    data_json = response

    return jsonify({'message': f'Webhook recebido com sucesso!{data_json}'}), 200

if __name__ == '__main__':
    app.run(debug=True)
