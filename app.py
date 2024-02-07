from flask import Flask, request, jsonify
from discord_webhook import DiscordWebhook, DiscordEmbed

app = Flask(__name__)

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    github_event = request.headers.get('X-GitHub-Event')

    github_payload = request.json

    # Extrair informações relevantes do payload do GitHub
    repository_name = github_payload['repository']['full_name']
    branch_name = github_payload['ref'].split('refs/heads/')[-1]
    commit_author = github_payload['head_commit']['author']['name']
    commit_message = github_payload['head_commit']['message']
    commit_id = github_payload['head_commit']['id']
    commit_url = github_payload['head_commit']['url']
    author_name = github_payload['sender']['login']
    author_avatar_url = github_payload['sender']['avatar_url']
    author_url = github_payload['sender']['html_url']
    commit_changes = {
        'Arquivos adicionados': github_payload['head_commit']['added'],
        'Arquivos alterados': github_payload['head_commit']['modified'],
        'Arquivos excluídos': github_payload['head_commit']['removed']
    }

    # Criar o embed para o Discord
    embed = DiscordEmbed(
        title=f'{repository_name} - {branch_name}',
        description=commit_message,
        color='9900ff'
    )
    embed.set_author(
        name=f'{commit_author} - @{author_name}',
        icon_url=author_avatar_url,
        url=author_url
    )

    embed.set_footer(text=f'Commit ➡️ {commit_id}')
    embed.set_timestamp()

    # Adicionar campos para as alterações
    for tipo, arquivos in commit_changes.items():
        if arquivos:

            if tipo == 'Arquivos adicionados':
                color = '32'
            elif tipo == 'Arquivos alterados':
                color = '33'
            else:
                color = '31'

            arquivos_str = '\n'.join(arquivos)

            valueText = f"```ansi\n\u001b[0;{color}m{arquivos_str}\n```"
            embed.add_embed_field(name=tipo, value=valueText, inline=False)

    embed.url = commit_url

    # Enviar o embed para o canal no Discord
    webhook_url = 'https://discord.com/api/webhooks/1204507570979475496/ox5XYN67s1bBfn1zUUYgYRGnC9UgFhVRPIFES52wTykAfryu0jmACzOVJ3z64Xkic9vT'
    webhook = DiscordWebhook(url=webhook_url)
    webhook.add_embed(embed)
    response = webhook.execute()

    return jsonify({'message': 'Webhook recebido com sucesso!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
