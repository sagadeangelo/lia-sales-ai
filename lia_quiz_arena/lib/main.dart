import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const LiaQuizArenaApp());
}

class LiaQuizArenaApp extends StatelessWidget {
  const LiaQuizArenaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'LIA Quiz Arena',
      theme: ThemeData.dark(),
      home: const QuizScreen(),
    );
  }
}

class QuizScreen extends StatefulWidget {
  const QuizScreen({super.key});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {

  Map<String, dynamic>? question;

  bool loading = true;

  int xp = 0;

  int streak = 0;

  String resultMessage = "";

  @override
  void initState() {
    super.initState();
    loadQuestion();
  }

  Future<void> loadQuestion() async {

    try {

      setState(() {
        loading = true;
      });

      final response = await http.get(
        Uri.parse(
          'https://arena.lasagadeangelo.com.mx/quiz/question',
        ),
      );

      final data = jsonDecode(response.body);

      setState(() {

        question = Map<String, dynamic>.from(
          data["question"],
        );

        loading = false;
      });

    } catch (e) {

      print(e);

      setState(() {
        loading = false;
      });
    }
  }

  Future<void> answerQuestion(String answer) async {

    try {

      final response = await http.post(
        Uri.parse(
          'https://arena.lasagadeangelo.com.mx/quiz/answer',
        ),
        headers: {
          "Content-Type": "application/json"
        },
        body: jsonEncode({
          "question_id": question!["id"],
          "selected_answer": answer
        }),
      );

      final data = jsonDecode(response.body);

      bool correct = data["result"]["correct"];

      setState(() {

        if (correct) {

          xp += 10;
          streak++;

          resultMessage =
              "🔥 Correcto +10 XP";

        } else {

          streak = 0;

          resultMessage =
              "❌ Incorrecto";
        }
      });

      await Future.delayed(
        const Duration(seconds: 2),
      );

      setState(() {
        resultMessage = "";
      });

      loadQuestion();

    } catch (e) {

      print(e);
    }
  }

  @override
  Widget build(BuildContext context) {

    final width =
        MediaQuery.of(context).size.width;

    final isMobile = width < 700;

    return Scaffold(

      backgroundColor: const Color(0xFF050510),

      body: SafeArea(

        child: loading

            ? const Center(
                child: CircularProgressIndicator(),
              )

            : question == null

                ? const Center(
                    child: Text(
                      "Error loading question",
                    ),
                  )

                : SingleChildScrollView(

                    child: Padding(
                      padding: const EdgeInsets.all(18),

                      child: Column(

                        children: [

                          const SizedBox(height: 10),

                          Image.asset(
                            'assets/images/lia_logo.png',
                            height: 80,
                          ),

                          const SizedBox(height: 10),

                          const Text(
                            "LIA Quiz Arena",

                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                            ),
                          ),

                          const SizedBox(height: 20),

                          Row(
                            mainAxisAlignment:
                                MainAxisAlignment.center,

                            children: [

                              _topBadge(
                                "⭐ XP",
                                xp.toString(),
                              ),

                              const SizedBox(width: 15),

                              _topBadge(
                                "🔥 Streak",
                                streak.toString(),
                              ),
                            ],
                          ),

                          const SizedBox(height: 30),

                          Container(

                            width: isMobile
                                ? double.infinity
                                : 750,

                            padding:
                                const EdgeInsets.all(25),

                            decoration: BoxDecoration(

                              borderRadius:
                                  BorderRadius.circular(30),

                              gradient: LinearGradient(
                                colors: [
                                  Colors.grey.shade900,
                                  const Color(0xFF191933),
                                ],
                              ),

                              border: Border.all(
                                color: Colors.cyanAccent,
                                width: 2,
                              ),

                              boxShadow: [

                                BoxShadow(
                                  color:
                                      Colors.cyanAccent
                                          .withOpacity(0.3),

                                  blurRadius: 25,
                                ),
                              ],
                            ),

                            child: Column(

                              children: [

                                Text(
                                  question!["question"]
                                      .toString(),

                                  textAlign:
                                      TextAlign.center,

                                  style:
                                      TextStyle(
                                    fontSize:
                                        isMobile
                                            ? 28
                                            : 40,

                                    fontWeight:
                                        FontWeight.bold,

                                    height: 1.2,
                                  ),
                                ),

                                const SizedBox(height: 35),

                                GridView.builder(

                                  shrinkWrap: true,

                                  physics:
                                      const NeverScrollableScrollPhysics(),

                                  itemCount:
                                      (question!["options"]
                                              as List)
                                          .length,

                                  gridDelegate:
                                      SliverGridDelegateWithFixedCrossAxisCount(

                                    crossAxisCount:
                                        isMobile ? 1 : 2,

                                    crossAxisSpacing: 20,

                                    mainAxisSpacing: 20,

                                    childAspectRatio:
                                        isMobile
                                            ? 3.5
                                            : 2.3,
                                  ),

                                  itemBuilder:
                                      (context, index) {

                                    final option =
                                        question!["options"]
                                            [index]
                                            .toString();

                                    return GestureDetector(

                                      onTap: () {
                                        answerQuestion(
                                          option,
                                        );
                                      },

                                      child: AnimatedContainer(

                                        duration:
                                            const Duration(
                                          milliseconds: 300,
                                        ),

                                        decoration:
                                            BoxDecoration(

                                          borderRadius:
                                              BorderRadius.circular(
                                            24,
                                          ),

                                          gradient:
                                              const LinearGradient(
                                            colors: [
                                              Color(
                                                0xFF202040,
                                              ),
                                              Color(
                                                0xFF131326,
                                              ),
                                            ],
                                          ),

                                          border: Border.all(
                                            color:
                                                Colors.white12,
                                          ),

                                          boxShadow: [

                                            BoxShadow(
                                              color:
                                                  Colors.black
                                                      .withOpacity(
                                                0.5,
                                              ),

                                              blurRadius: 12,
                                            ),
                                          ],
                                        ),

                                        child: Stack(

                                          children: [

                                            Positioned(

                                              right: -10,
                                              bottom: -10,

                                              child: Opacity(

                                                opacity: 0.08,

                                                child:
                                                    Image.asset(
                                                  'assets/images/lia_logo.png',
                                                  width: 100,
                                                ),
                                              ),
                                            ),

                                            Center(

                                              child: Padding(
                                                padding:
                                                    const EdgeInsets
                                                        .all(12),

                                                child: Text(
                                                  option,

                                                  textAlign:
                                                      TextAlign
                                                          .center,

                                                  style:
                                                      TextStyle(
                                                    fontSize:
                                                        isMobile
                                                            ? 20
                                                            : 24,

                                                    fontWeight:
                                                        FontWeight
                                                            .w600,
                                                  ),
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    );
                                  },
                                ),

                                const SizedBox(height: 30),

                                AnimatedSwitcher(

                                  duration:
                                      const Duration(
                                    milliseconds: 300,
                                  ),

                                  child: Text(
                                    resultMessage,

                                    key:
                                        ValueKey(resultMessage),

                                    style: TextStyle(

                                      fontSize: 30,

                                      fontWeight:
                                          FontWeight.bold,

                                      color:
                                          resultMessage
                                                  .contains(
                                                "Correcto",
                                              )
                                              ? Colors
                                                  .greenAccent
                                              : Colors
                                                  .redAccent,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),

                          const SizedBox(height: 40),
                        ],
                      ),
                    ),
                  ),
      ),
    );
  }

  Widget _topBadge(
    String title,
    String value,
  ) {

    return Container(

      padding: const EdgeInsets.symmetric(
        horizontal: 22,
        vertical: 12,
      ),

      decoration: BoxDecoration(

        color: Colors.white10,

        borderRadius:
            BorderRadius.circular(20),

        border: Border.all(
          color: Colors.white12,
        ),
      ),

      child: Row(

        children: [

          Text(
            title,

            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(width: 10),

          Text(
            value,

            style: const TextStyle(
              fontSize: 18,
            ),
          ),
        ],
      ),
    );
  }
}