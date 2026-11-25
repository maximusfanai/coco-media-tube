import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  runApp(const CoCoMediaTubeApp());
}

class CoCoMediaTubeApp extends StatelessWidget {
  const CoCoMediaTubeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CoCo Media Tube',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF06060E),
      ),
      home: const MediaWebViewScreen(),
    );
  }
}

class MediaWebViewScreen extends StatefulWidget {
  const MediaWebViewScreen({super.key});

  @override
  State<MediaWebViewScreen> createState() => _MediaWebViewScreenState();
}

class _MediaWebViewScreenState extends State<MediaWebViewScreen> {
  late final WebViewController _controller;
  bool _isLoading = true;

  static const String _appUrl =
      'https://coco-media-tube-vrxj7agk3mecy2supgarzs.streamlit.app/';

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFF06060E))
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (_) => setState(() => _isLoading = true),
          onPageFinished: (_) => setState(() => _isLoading = false),
        ),
      )
      ..loadRequest(Uri.parse(_appUrl));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF06060E),
      body: SafeArea(
        child: Stack(
          children: [
            WebViewWidget(controller: _controller),
            if (_isLoading)
              const Center(
                child: CircularProgressIndicator(),
              ),
          ],
        ),
      ),
    );
  }
}
