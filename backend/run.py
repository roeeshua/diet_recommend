from app import create_app

app = create_app()

# 打印所有已注册的路由（调试用）
print("=" * 50)
print("已注册的路由：")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.methods} {rule}")
print("=" * 50)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)