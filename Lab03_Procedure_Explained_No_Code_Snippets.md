# Lab 03 Procedure Explanation: Concurrency and Synchronization

## Part I: Thread Fundamentals and Lifecycle

### Step 1: Opening the Linux terminal

I began by opening the Linux terminal so I could create files, compile C programs, run executables, and use Linux process-monitoring commands. This was the working environment for the entire lab because POSIX threads and process tools are normally tested from the command line.

### Step 2: Creating the first POSIX thread

I created the first C program using the POSIX Threads library. The program created a worker thread with `pthread_create`, and that worker thread was supposed to print a message.

What I observed was that the worker thread did not always print before the program ended. This happened because the main thread continued running immediately after creating the worker thread. Since the main thread reached the end of the program quickly, the process could terminate before the worker thread had a chance to execute.

The result showed that creating a thread only starts another execution path; it does not automatically make the main program wait for that thread.

### Step 3: Preventing premature exit with `sleep`

I modified the program so the main thread paused for five seconds after creating the worker thread. During that pause, the process stayed alive, and the worker thread had enough time to print its message.

The output showed the worker thread message before the final main-thread message. This confirmed that the worker thread was working correctly, but it also showed that `sleep` is not a good synchronization method. It only delays the main thread for a fixed amount of time, and that delay may be too short or unnecessarily long depending on the task.

### Step 4: Proper synchronization with `pthread_join`

I replaced the fixed delay with `pthread_join`. This made the main thread wait specifically for the worker thread to finish before continuing.

The output showed the worker thread completing first and the main thread exiting afterward. This result was better than using `sleep` because the main thread waited only as long as necessary. The program no longer depended on guessing how long the worker thread would take.

### Step 5: Monitoring threads in the operating system

I added process ID reporting to the program and kept the thread alive long enough to inspect it from a second terminal. While the program was running, I used the `ps -T -p` command with the process ID printed by the program.

The output showed two thread entries under the same process ID: one for the main thread and one for the worker thread. This proved that the operating system sees threads as separate execution units even though they belong to the same process.

### Step 6: Managing multiple threads

I expanded the program to create two worker threads running the same function. I also used two `pthread_join` calls so the main thread waited for both workers to finish.

The process inspection output showed three entries: the main thread plus two worker threads. Both worker threads slept at the same time, so the total runtime stayed around ten seconds instead of twenty. This showed that the two worker threads were running concurrently rather than one after the other.

### Step 7: Executing different tasks simultaneously

I modified the program so each thread ran a different function. This simulated a program doing two different jobs at the same time.

The output showed both task messages after the delay. In one run, task 1 printed before task 2, but that order is not guaranteed. Since both threads run concurrently, the scheduler decides which one gets CPU time first. The result showed that threads can perform independent tasks inside the same process.

## Part II: Threads vs. Processes and Memory Architecture

### Step 8: Comparing processes and threads

I wrote one program using `fork()` and another using `pthread_create`. Both programs produced two messages, so at first their output looked similar.

The important difference was how the second execution path was created. In the process program, `fork()` duplicated the process. In the thread program, `pthread_create` started new execution paths inside the same process. This step showed that similar-looking output can come from two very different memory models.

### Step 9: Verifying process IDs

I added process ID printing to both the process program and the thread program.

In the process program, the output showed two different process IDs because `fork()` created a child process separate from the parent. In the thread program, both messages showed the same process ID because both threads belonged to the same process. This confirmed that processes are independent execution containers, while threads are execution units inside one process.

### Step 10: Memory isolation in processes

I created a variable before calling `fork()`, then changed the variable only in the child process.

The output showed the child process with the updated value and the parent process with the original value. This proved that after `fork()`, the parent and child have separate memory. Even though the variable started with the same value in both processes, each process had its own copy after the fork.

### Step 11: Global variables in processes

I moved the variable outside of `main` so it became global, then repeated the process test.

The result was the same as the previous step. The child process showed the changed value, while the parent process still showed the original value. This proved that global variables are also copied when a process forks. A variable being global does not make it shared between different processes.

### Step 12: Shared memory in threads

I tested a global variable with two threads. One thread changed the global variable, and the other thread printed it afterward.

The output showed that both threads saw the updated value. This happened because threads share the same address space inside a process. This makes communication between threads easier than communication between processes, but it also creates risk because multiple threads can access or modify the same data at the same time.

## Part III: Critical Section and Race Condition

### Step 13: Basic shared counter

I created a shared counter named `mails` and used two threads to increment it once each.

The expected final value was 2, and the program reached that value. This small example worked because each thread only performed one increment, so there was little opportunity for a timing conflict.

### Step 14: Incrementing with a small loop

I increased the work so each thread incremented the counter 100 times.

The expected final value was 200, and the output showed 200. This still worked because the workload was small enough that the operating system often completed one thread's work without causing many overlapping updates.

### Step 15: Race condition with 1,000,000 iterations

I increased the workload to 1,000,000 increments per thread. The expected total was 2,000,000.

The output did not reach 2,000,000. Instead, the screenshots showed lower values such as 1,627,341 and 1,726,431. The value also changed between runs.

This happened because `mails++` is not atomic. The operation requires the CPU to read the current value, increment it, and write it back. If two threads read the same value before either writes the new value back, one increment is lost. The result was unpredictable because the thread scheduler can interrupt the threads at different moments each time the program runs.

## Part IV: Thread Synchronization and Mutex

### Step 16: Solving the race condition with a mutex

I added a mutex to protect the counter update. The increment operation became a critical section, meaning only one thread could execute it at a time.

After adding the lock and unlock around the shared counter update, the output became consistent. The program reached the expected total because the mutex prevented two threads from modifying `mails` at the same time. The result showed that mutexes protect data integrity, although they can add waiting time because threads may have to pause for the lock.

### Step 17: Scaling to multiple threads

I increased the number of threads from two to four while keeping the mutex protection.

The expected final value was 4,000,000 because each of the four threads incremented the counter 1,000,000 times. The screenshot showed the correct final value of 4,000,000. This confirmed that the mutex solution scaled correctly. However, more threads also meant more lock contention because all four threads were competing to enter the same critical section.

### Step 18: Verification by removing the lock

I removed the mutex protection while keeping the four-thread version of the program.

The output became incorrect again. Instead of reaching 4,000,000, the screenshot showed a much lower value such as 1,738,421. This proved that the mutex was the reason the previous step worked. Without the lock, the shared counter was corrupted by simultaneous updates. The program may run faster without synchronization, but the result is not reliable.

## Part V: Semaphores and Resource Management

### Step 19: Introduction to POSIX semaphores

I created a semaphore program with four threads. Each thread received its own ID, and the semaphore was initialized, but it was not yet used to block or control access.

The output showed the threads printing freely. This happened because simply creating a semaphore does not affect the program until the code uses `sem_wait` and `sem_post`. I also observed why dynamically allocating each thread ID matters: if all threads used the address of the same loop variable, they might all read the wrong or final value.

### Step 20: Adding semaphore operations

I added semaphore wait and post operations around the section where each thread printed its message.

With the semaphore initialized to 1, only one thread could enter the protected section at a time. This made the semaphore act like a mutex. The result showed that semaphores can be used to control access to a shared section of code.

### Step 21: Implementing `sem_wait` and `sem_post`

I placed a one-second delay inside the semaphore-protected section. Since the semaphore value was 1, only one thread could enter that section at a time.

The output appeared one thread at a time, and the whole program took about four seconds because four threads each spent one second in the protected section. This showed that `sem_wait` decreases the semaphore count and blocks when no permits are available, while `sem_post` releases a permit for another thread.

### Step 22: Multiple access with counting semaphores

I changed the semaphore's initial value from 1 to 3.

This allowed up to three threads to enter the protected section at the same time. The fourth thread had to wait until one of the first three finished and released a permit. The output order was not always the same because the scheduler still decided which thread ran first. The result showed the main difference between a mutex and a counting semaphore: a mutex allows one thread at a time, while a semaphore can allow a limited number of threads at once.

## Image Explanations

1. `image1.jpeg`: This image shows the UTRGV logo used on the title page. It identifies the university connected to the lab report.
2. `image2.png`: This screenshot shows the first thread program being edited in nano. It represents the first attempt to create a worker thread.
3. `image3.png`: This screenshot shows compiling and running the first thread program. The output demonstrates that the main program can finish before the worker thread prints.
4. `image4.png`: This screenshot shows the version that used `sleep`. The worker thread printed successfully because the main thread paused before exiting.
5. `image5.png`: This screenshot shows the version using `pthread_join`. The main thread waited for the worker thread to finish before printing the final message.
6. `image6.png`: This screenshot shows the operating system listing the main thread and one worker thread under the same process ID.
7. `image7.png`: This screenshot shows three thread entries: the main thread and two worker threads. It confirms that multiple threads existed inside one process.
8. `image8.png`: This screenshot shows two different task functions completing. In that run, task 1 printed before task 2.
9. `image9.png`: This screenshot shows the process ID and thread listing while the two-task program was running. It confirms that the two task threads were active at the same time.
10. `image10.png`: This screenshot shows both thread messages reporting the same process ID. It confirms that threads share one process.
11. `image11.png`: This screenshot shows the process version reporting different process IDs. It confirms that `fork()` creates separate processes.
12. `image12.png`: This screenshot shows the global-variable process test. One process reported `Global X: 3`, while the other reported `Global X: 2`, proving the global variable was copied rather than shared.
13. `image13.png`: This screenshot shows both threads seeing the updated value of `x`. It proves that threads share global variables.
14. `image14.png`: This screenshot shows a race-condition result where the counter was lower than expected. The missing increments were caused by unsynchronized shared access.
15. `image15.png`: This screenshot shows the small-loop counter result of 200. In that case, the expected result was reached.
16. `image16.png`: This screenshot shows another race-condition result with a different incorrect count. The changing number shows that the result depends on timing.
17. `image17.png`: This screenshot shows the mutex-protected four-thread result of 4,000,000. It confirms that the mutex protected the counter correctly.
18. `image18.png`: This screenshot shows the four-thread program without mutex protection. The lower result confirms that the race condition returned.
19. `image19.png`: This screenshot shows semaphore thread messages being printed. It demonstrates that all four threads ran.
20. `image20.png`: This screenshot shows semaphore-controlled output where thread messages appear under controlled access.
21. `image21.png`: This screenshot shows all four semaphore thread messages. It confirms that each thread executed.
22. `image22.png`: This screenshot shows a different order of semaphore thread output. The changed order shows that thread scheduling is nondeterministic.

## Results Summary

The lab demonstrated how threads are created, synchronized, and observed in Linux. The first part showed that `pthread_create` starts a new thread, but the main thread must use `pthread_join` if it needs to wait correctly.

The process and thread comparison showed that processes have separate memory, while threads share memory inside the same process. This makes threads efficient for communication, but it also makes shared data dangerous when multiple threads update it at the same time.

The race-condition tests showed that shared counter updates can produce incorrect results because incrementing a variable is not atomic. The mutex fixed the problem by allowing only one thread into the critical section at a time. The semaphore section showed another synchronization method, where the initial semaphore value controls how many threads may enter a protected section at once.
