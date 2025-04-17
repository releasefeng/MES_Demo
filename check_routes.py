from app import create_app

app = create_app()

print("\n已注册的路由:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]") 