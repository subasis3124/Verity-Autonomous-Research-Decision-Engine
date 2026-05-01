import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/query_provider.dart';
import '../models/query_model.dart';
import 'login_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<QueryProvider>(context, listen: false).loadQueries();
    });
  }

  Widget _buildStatusBadge(String status) {
    Color bg;
    Color fg;
    String label = status.toUpperCase();

    switch (status) {
      case 'completed':
        bg = Colors.green.withOpacity(0.2);
        fg = Colors.greenAccent;
        break;
      case 'failed':
        bg = Colors.red.withOpacity(0.2);
        fg = Colors.redAccent;
        break;
      case 'processing':
      case 'pending':
      default:
        bg = Colors.amber.withOpacity(0.2);
        fg = Colors.amberAccent;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: fg.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(color: fg, fontSize: 10, fontWeight: FontWeight.bold),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final queryProvider = Provider.of<QueryProvider>(context);

    // Provide safety net redirect if logged out
    if (!auth.isAuthenticated) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const LoginScreen()),
        );
      });
      return const Scaffold(backgroundColor: Color(0xFF0F172A));
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        title: const Text('Verity Dashboard', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.white70),
            onPressed: () async {
              await auth.logout();
              Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const LoginScreen()));
            },
          )
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => queryProvider.loadQueries(),
        child: queryProvider.isLoading && queryProvider.queries.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: queryProvider.queries.length,
                itemBuilder: (context, index) {
                  final QueryModel q = queryProvider.queries[index];
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.blueGrey.withOpacity(0.1)),
                    ),
                    child: ListTile(
                      contentPadding: const EdgeInsets.all(16),
                      title: Text(
                        q.rawQuery,
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500, height: 1.4),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      subtitle: Padding(
                        padding: const EdgeInsets.only(top: 12.0),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              q.createdAt.toString().split('.')[0],
                              style: TextStyle(color: Colors.blueGrey[400], fontSize: 12),
                            ),
                            _buildStatusBadge(q.status),
                          ],
                        ),
                      ),
                      onTap: () {
                         // Navigation to Query Detail goes here
                      },
                      trailing: IconButton(
                        icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
                        onPressed: () => queryProvider.deleteQuery(q.id),
                      ),
                    ),
                  );
                },
              ),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: const Color(0xFF38BDF8),
        child: const Icon(Icons.add, color: Colors.white),
        onPressed: () {
          _showSubmitDialog(context, queryProvider);
        },
      ),
    );
  }

  void _showSubmitDialog(BuildContext context, QueryProvider provider) {
    final ctrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('New Research Query', style: TextStyle(color: Colors.white)),
        content: TextField(
          controller: ctrl,
          style: const TextStyle(color: Colors.white),
          minLines: 3,
          maxLines: 5,
          decoration: const InputDecoration(
            hintText: 'Enter your question...',
            hintStyle: TextStyle(color: Colors.white38),
            filled: true,
            fillColor: Color(0xFF0F172A),
            border: OutlineInputBorder(borderSide: BorderSide.none),
          ),
        ),
        actions: [
          TextButton(
            child: const Text('Cancel', style: TextStyle(color: Colors.white54)),
            onPressed: () => Navigator.pop(ctx),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF38BDF8)),
            child: const Text('Submit', style: TextStyle(color: Colors.white)),
            onPressed: () async {
              if (ctrl.text.isEmpty) return;
              Navigator.pop(ctx);
              await provider.submitQuery(ctrl.text);
            },
          )
        ],
      ),
    );
  }
}
