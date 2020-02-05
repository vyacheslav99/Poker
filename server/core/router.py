import controllers

roadmap = {}

def build_roadmap():
    for cls in dir(controllers):
        obj = controllers.__dict__[cls]

        try:
            for field in obj.__dict__:
                if not field.startswith('_') and type(obj.__dict__[field]) == staticmethod:
                    sm = eval(f'controllers.{cls}.{field}')
                    doc = sm.__doc__

                    if doc:
                        route = None
                        methods = None

                        for ln in doc.split('\n'):
                            if ':route:' in ln:
                                route = ln.split(':route:')[1].strip().lower()
                            if ':methods:' in ln:
                                methods = ln.split(':methods:')[1].strip().split(',')

                        if route:
                            if methods:
                                roadmap[route] = {}
                                for method in methods:
                                    roadmap[route][method.lower()] = sm
                            else:
                                roadmap[route] = sm
        except Exception:
            pass

build_roadmap()
