import 'package:flutter/material.dart';
import '../models/estacion.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'login_screen.dart';
import 'add_estacion_screen.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Estacion>> futureEstaciones;
  final ApiService apiService = ApiService();

  @override
  void initState() {
    super.initState();
    futureEstaciones = apiService.fetchEstaciones();
  }

  void _refrescar() {
    setState(() {
      futureEstaciones = apiService.fetchEstaciones();
    });
  }

  void _mostrarDialogoEdicion(Estacion estacion) {
    final nombreCtrl = TextEditingController(text: estacion.nombre);
    final ubicacionCtrl = TextEditingController(text: estacion.ubicacion);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Editar Estación"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nombreCtrl,
              decoration: const InputDecoration(labelText: "Nombre"),
            ),
            TextField(
              controller: ubicacionCtrl,
              decoration: const InputDecoration(labelText: "Ubicación"),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancelar"),
          ),
          ElevatedButton(
            onPressed: () async {
              bool ok = await apiService.editarEstacion(
                estacion.id,
                nombreCtrl.text,
                ubicacionCtrl.text,
              );
              if (ok) {
                Navigator.pop(context);
                _refrescar();
              }
            },
            child: const Text("Guardar"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Estaciones SMAT'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await AuthService().logout();
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
                (route) => false,
              );
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Estacion>>(
        future: futureEstaciones,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('❌ ${snapshot.error}'));
          } else {
            return RefreshIndicator(
              onRefresh: () async => _refrescar(),
              child: ListView.builder(
                itemCount: snapshot.data!.length,
                itemBuilder: (context, index) {
                  final est = snapshot.data![index];
                  return Dismissible(
                    key: Key(est.id.toString()),
                    direction: DismissDirection.endToStart,
                    background: Container(
                      color: Colors.red,
                      alignment: Alignment.centerRight,
                      padding: const EdgeInsets.only(right: 20),
                      child: const Icon(Icons.delete, color: Colors.white),
                    ),
                    onDismissed: (direction) async {
                      await apiService.eliminarEstacion(est.id);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text("${est.nombre} eliminada")),
                      );
                    },
                    child: ListTile(
                      leading: const Icon(Icons.satellite_alt),
                      title: Text(est.nombre),
                      subtitle: Text(est.ubicacion),
                      onTap: () => _mostrarDialogoEdicion(est),
                    ),
                  );
                },
              ),
            );
          }
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          await Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AddEstacionScreen()),
          );
          _refrescar();
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}