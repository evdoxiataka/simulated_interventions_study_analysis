from matplotlib.lines import Line2D
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
import arviz as az
import matplotlib.pyplot as plt
from matplotlib.text import Annotation
import numpy as np
import seaborn as sns
from adjustText import adjust_text

from utils.information_retrieval import get_task, join_rqs

## COMBINED FOREST PLOT
def combined_forest_plot(forrest_plot_data):
    """
     forrest_plot_data: Dict{<axis_id>:{"title":<>,"traces":[],"var":<>,"ref_val":0}}
     Each axis_id correponds to a column in the forest plot.
    """
    ## global settings
    plt.rc('xtick', labelsize=20) 
    plt.rc('ytick', labelsize=20) 
    plt.rcParams.update({'font.size': 14.5})
    fig, axes = plt.subplots(1, len(forrest_plot_data))
    fig.set_figheight(16)
    fig.set_figwidth(20)
    fontsize = 20
    
    ## coloured by research question
    colors = ['skyblue', 'blue', 'blue', 'blue', 'navy',
              'skyblue', 'blue', 'blue', 'blue', 'navy', 'navy',
              'skyblue', 'skyblue', 'blue', 'blue', 'blue', 'blue', 'navy', 'navy']

    ## convert the data into a list of per-task traces
    for i, ax in enumerate(axes):
        if 'traces' in forrest_plot_data[i]:
            dat = join_rqs(forrest_plot_data[i]['traces'], 
                       forrest_plot_data[i]['var'])
        elif 'data' in forrest_plot_data[i]:
            dat = forrest_plot_data[i]['data']
        az.plot_forest(dat, ax=ax, colors=colors, linewidth = 3)
        ## set titles
        ax.set_title(forrest_plot_data[i]['title'])
        ## add ref lines
        if forrest_plot_data[i]['ref_val'] is not None: 
            ax.vlines([forrest_plot_data[i]['ref_val']],
                      *ax.get_ylim(), 
                      colors='k', 
                      zorder=0, 
                      linewidth = 0.5)
        ## dividing lines for each problem, at task 5->6 and task 11->12
        y_pts = [line.get_ydata()[0] for line in ax.lines]    
        # ax.axhline(y_pts[-5]-12, c='grey')            
        # ax.axhline(y_pts[-11]-12, c='grey')
        ax.patches[1].set_color('darkgray')
        if i==0:
            ## Problem annotation
            ax.set_yticklabels([f't{19-i}' for i in range(19)]);
            ax.text(0.1,y_pts[-6]-8,  'Model 2', c='k', fontsize=fontsize)    
            ax.text(0.1,y_pts[-12]-8,  'Model 3', c='k', fontsize=fontsize)  
            ax.text(0.1,y_pts[-1]+8,  'Model 1', c='k', fontsize=fontsize)  
            continue
        ## disable yaxis except of first column
        ax.get_yaxis().set_visible(False)

    ## set legend
    custom_lines = [Line2D([0], [0], color='skyblue', lw=3),
                    Line2D([0], [0], color='blue', lw=3),
                    Line2D([0], [0], color='navy', lw=3)]
    axes[-4].legend(custom_lines, ["T1", "T2", "T3"],
               prop={'size': fontsize-3})

    plt.draw()
    plt.show()

    #save figure
    # fig.savefig("Figure8a.svg", dpi=300)
    return axes

## ORDERED FOREST PLOTS OF DIFFERENCES
def order_tasks(datasets):   
    dic = {}
    for s in datasets:        
        for t in s.task:
            dic[str(t.values)] = s.sel(task = t).to_numpy().mean()
    return list(dict(sorted(dic.items(), key=lambda item: item[1])).keys())
            
# return a list of flat numpy traces, one per task
def order_tasks_colors(rqs, var_name, colors):
    datasets = [az.convert_to_dataset(rq)[var_name] 
                for rq in rqs] 
    ordered_tasks = order_tasks(datasets)
    tasks = [np.array(get_task(datasets,  
                               task=t)).ravel() 
             for t in ordered_tasks]
    cols = [colors[t] for t in ordered_tasks]
    return tasks, cols, ordered_tasks

def combined_oredered_forest_plot(forrest_plot_data):
    """
     forrest_plot_data: Dict{<axis_id>:{"title":<>,"traces":[],"var":<>,"ref_val":0}}
     Each axis_id correponds to a column in the forest plot.
    """
    ## global settings
    plt.rc('xtick', labelsize=20) 
    plt.rc('ytick', labelsize=20) 
    plt.rcParams.update({'font.size': 14.5})
    fig, axes = plt.subplots(1, len(forrest_plot_data))
    fig.set_figheight(16)
    fig.set_figwidth(20)
    fontsize = 20
    
    ## coloured by research question
    colors_dict = {"t1":'skyblue',"t2":'blue',"t3":'blue',"t4":'blue',"t5":'navy',
              "t6":'skyblue',"t7":'blue',"t8":'blue',"t9":'blue',"t10":'navy',"t11":'navy',
              "t12":'skyblue',"t13":'skyblue',"t14":'blue',"t15":'blue',"t16":'blue',"t17":'blue',"t18":'navy',"t19":'navy'}

    ## convert the data into a list of per-task traces
    for i, ax in enumerate(axes):
        if 'traces' in forrest_plot_data[i]:
            dat, colors, ordered_tasks = order_tasks_colors(forrest_plot_data[i]['traces'], 
                       forrest_plot_data[i]['var'], colors_dict)
        elif 'data' in forrest_plot_data[i]:
            dat = forrest_plot_data[i]['data']
        az.plot_forest(dat, ax=ax, colors=colors, linewidth = 3)
        ## set titles
        ax.set_title(forrest_plot_data[i]['title'])
        ## add ref lines
        if forrest_plot_data[i]['ref_val'] is not None: 
            ax.vlines([forrest_plot_data[i]['ref_val']],
                      *ax.get_ylim(), 
                      colors='k', 
                      zorder=0, 
                      linewidth = 0.5)
        for patch in ax.patches:
            patch.set_color('white')
        ax.set_yticklabels(ordered_tasks[::-1])

    plt.draw()
    plt.show()

    #save figure
    # fig.savefig("Figure9.svg", dpi=300)
    return axes

## PAIR PLOT
def add_labels(ax, x,y,labels,colors):
    alpha = 0.6
    texts = []
    for i,pair in enumerate(zip(x,y)):
        texts.append(ax.text(pair[0], pair[1], labels[i], fontsize = 18, color = colors[i], alpha = alpha))
    adjust_text(texts, 
                ax=ax, 
                lim=2000, 
                text_from_points = True, 
                text_from_text = True, 
                autoalign = 'y',
                expand_text = (1.05, 1.2), 
                expand_points = (1.05, 1.2),
                expand_objects = (1.05, 1.2), 
                force_text = (0.1, 0.25), 
                force_points = (0.2, 0.5),
                force_objects  = (0.1, 0.25),
                precision  = 0.002,
                # precision  = 0.,
                arrowprops = dict(arrowstyle="-", color='gray', lw=0.5, alpha = alpha))
    annotations = [child for child in ax.get_children() if isinstance(child, Annotation)]
    for i, arrow in enumerate(annotations):
        arrow.arrow_patch.set(color = colors[i])

def pair_plot_of_means(df, pp_data):
    ## global settings
    plt.figure()
    plt.rcParams['axes.xmargin'] = 0.01
    plt.rcParams['axes.ymargin'] = 0.01
    plt.rcParams.update({'font.size': 20})    
    ##
    g = sns.PairGrid(df, 
                     corner=True,
                     vars = ['accuracy','response_time','confidence'],
                     diag_sharey = False, 
                     )
    g.map_diag(sns.kdeplot,
              fill = False,
              )
    g.map_lower(sns.regplot,
                ci = 90,
                # truncate = False,
                scatter_kws = {"s":100,'alpha':0.7,"color":None,"c":df['color']},
                line_kws = {"color":"magenta", 'zorder':0, 'linewidth':2}, 
                label = [1,2,3]
               )
    
    g.fig.axes[6].lines.pop(0)
    g.fig.axes[7].lines.pop(0)
    g.fig.axes[8].lines.pop(0)
    
    sns.kdeplot(x = df["accuracy"],
                hue = df["Research Question"],
                legend = False,
                fill = False,
                common_norm = False,
                palette={"RQ1":"skyblue","RQ2":"blue","RQ3":"navy"},
                ax = g.fig.axes[6]
                    )
    sns.kdeplot(x = df["response_time"],
                hue = df["Research Question"],
                legend = False,
                fill = False,
                common_norm = False,
                palette={"RQ1":"skyblue","RQ2":"blue","RQ3":"navy"},
                ax = g.fig.axes[7]
               )
    sns.kdeplot(x = df["confidence"],
                hue = df["Research Question"],
                legend = False,
                fill = False,
                common_norm = False,
                palette={"RQ1":"skyblue","RQ2":"blue","RQ3":"navy"},
                ax = g.fig.axes[8]
               )   

    ## plot vertical ref lines
    g.fig.axes[0].vlines([0],*g.fig.axes[0].get_ylim(), colors='k', zorder=0, linewidth = 0.5)
    g.fig.axes[1].vlines([0],*g.fig.axes[1].get_ylim(), colors='k', zorder=0, linewidth = 0.5)
    g.fig.axes[2].vlines([0],*g.fig.axes[2].get_ylim(), colors='k', zorder=0, linewidth = 0.5)
    g.fig.axes[3].vlines([0],*g.fig.axes[3].get_ylim(), colors='k', zorder=0, linewidth = 0.5)
    g.fig.axes[4].vlines([0],*g.fig.axes[4].get_ylim(), colors='k', zorder=0, linewidth = 0.5)
    g.fig.axes[5].vlines([0],*g.fig.axes[5].get_ylim(), colors='k', zorder=0, linewidth = 0.5)
    ## plot horizonal ref lines
    g.fig.axes[1].hlines([0],*g.fig.axes[1].get_xlim(), colors='k', zorder=0, linewidth = 0.5)
    g.fig.axes[3].hlines([0],*g.fig.axes[3].get_xlim(), colors='k', zorder=0, linewidth = 0.5)
    g.fig.axes[4].hlines([0],*g.fig.axes[4].get_xlim(), colors='k', zorder=0, linewidth = 0.5)

    ## set legend
    # g._legend.remove()
    custom_lines = [plt.scatter([], [], color='skyblue',label = 'T1', lw=2),
                    plt.scatter([], [], color='blue',label = 'T2', lw=2),
                    plt.scatter([], [], color='navy',label = 'T3', lw=2)]
    g.fig.axes[0].legend(handles = custom_lines, loc='upper right', 
               prop={'size': 20})

    ## label points
    add_labels(g.fig.axes[1], pp_data['accuracy'],pp_data['response_time'],pp_data['task'],pp_data['color'])
    add_labels(g.fig.axes[4], pp_data['response_time'],pp_data['confidence'],pp_data['task'],pp_data['color'])
    add_labels(g.fig.axes[3], pp_data['accuracy'],pp_data['confidence'],pp_data['task'],pp_data['color'])
    
    ## axis labels
    g.fig.axes[1].set_ylabel('Response Times IG-SG \n mean $\it{effect\_size}$')
    g.fig.axes[3].set_xlabel('Accuracy IG-SG \n mean $\it{diff\_of\_thetas}$')
    g.fig.axes[3].set_ylabel('Confidence IG-SG \n mean $\it{diff\_of\_means}$')
    g.fig.axes[4].set_xlabel('Response Times IG-SG \n mean $\it{effect\_size}$')
    g.fig.axes[5].set_xlabel('Confidence IG-SG \n mean $\it{diff\_of\_means}$')
    
    ## set figure size
    g.fig.set_figwidth(18)
    g.fig.set_figheight(15)
    ## save figure
    # g.fig.savefig('Figure8b.svg', dpi = 300)

def pair_plot_response_interaction(df, pp_data):
    g = sns.pairplot(df, hue = 'Task Type', kind='scatter',  
                 x_vars = ['accuracy','response_time','confidence'], 
                 y_vars = ['num_boxes','len_boxes'], 
                palette = {"T1":'skyblue',"T2":"blue","T3":"navy"},
                 plot_kws={"s":80})
    #set legend
    g._legend.remove()
    custom_lines = [plt.scatter([0], [0], color='skyblue', lw=2),
                    plt.scatter([0], [0], color='blue', lw=2),
                    plt.scatter([0], [0], color='navy', lw=2)]
    g.fig.axes[5].legend(custom_lines, ["T1", "T2", "T3"], loc='lower right', 
               prop={'size': 10})
#     plt.xscale('log')
#     plt.yscale('log')

def scatter_plot_of_num_len_boxes(df):
    g = sns.scatterplot(x='num_boxes', y='len_boxes', hue='Task Type', palette = {"T1":'skyblue',"T2":"blue","T3":"navy"}, data=df) 
    