python = find_program('python3')

current_dir = meson.current_source_dir()

foreach test_file : run_command('ls').stdout().split()
  if test_file.startswith('test_') and test_file.endswith('.py')
     test_suffix = test_file.split('_')[1]
     test_name = test_suffix.split('.py')[0]

     test(test_name,
          python, args : ['-m', 'unittest', test_file.strip()],
          workdir: current_dir)
  endif
endforeach
